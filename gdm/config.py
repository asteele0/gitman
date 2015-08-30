"""Wrappers for the dependency configuration files."""

import os
import sys
import shutil
import logging

import yorm

from . import common
from .shell import ShellMixin, GitMixin

logging.getLogger('yorm').setLevel(logging.INFO)
log = common.logger(__name__)


@yorm.attr(repo=yorm.converters.String)
@yorm.attr(dir=yorm.converters.String)
@yorm.attr(rev=yorm.converters.String)
@yorm.attr(link=yorm.converters.String)
class Source(yorm.converters.AttributeDictionary, ShellMixin, GitMixin):

    """A dictionary of `git` and `ln` arguments."""

    def __init__(self, repo, dir, rev='master', link=None):  # pylint: disable=W0622
        super().__init__()
        self.repo = repo
        self.dir = dir
        self.rev = rev
        self.link = link
        if not self.repo:
            raise ValueError("'repo' missing on {}".format(repr(self)))
        if not self.dir:
            raise ValueError("'dir' missing on {}".format(repr(self)))

    def __repr__(self):
        return "<source {}>".format(self)

    def __str__(self):
        fmt = "'{r}' @ '{v}' in '{d}'"
        if self.link:
            fmt += " <- '{s}'"
        return fmt.format(r=self.repo, v=self.rev, d=self.dir, s=self.link)

    def update_files(self, force=False, clean=True):
        """Ensure the source matches the specified revision."""
        log.info("updating source files...")

        # Enter the working tree
        if not os.path.exists(self.dir):
            self.mkdir(self.dir)
        self.cd(self.dir)
        if not os.path.exists('.git'):  # create it if needed
            log.debug("creating a new repository...")
            self.git_create()
        elif not force:  # exit if there are changes
            log.debug("confirming there are no uncommitted changes...")
            if self.git_changes():
                sys.exit("\n" + "uncommitted changes"
                         " ('--force' to overwrite): {}".format(os.getcwd()))

        # Fetch the desired revision
        self.git_fetch(self.repo, self.rev)

        # Update the working tree to the desired revision
        self.git_update(self.rev, clean=clean)

    def create_link(self, root, force=False):
        """Create a link from the target name to the current directory."""
        if self.link:
            log.info("creating a symbolic link...")
            target = os.path.join(root, self.link)
            source = os.path.relpath(os.getcwd(), os.path.dirname(target))
            if os.path.islink(target):
                os.remove(target)
            elif os.path.exists(target):
                if force:
                    shutil.rmtree(target)
                else:
                    sys.exit("\n" + "preexisting link location"
                             " ('--force' to overwrite): {}".format(target))
            self.ln(source, target)

    def identify(self):
        """Get the path and current repository URL and hash."""
        path = os.path.join(os.getcwd(), self.dir)

        if os.path.isdir(path):

            self.cd(path, visible=False)

            path = os.getcwd()
            url = self.git_get_url()
            if self.git_changes():
                sha = "<dirty>"
            else:
                sha = self.git_get_sha()

            return path, url, sha

        else:

            return path, "<missing>", "<unknown>"


@yorm.attr(repo=yorm.converters.String)
@yorm.attr(dir=yorm.converters.String)
@yorm.attr(rev=yorm.converters.String)
@yorm.attr(link=yorm.converters.String)
class LockedSource(Source):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sources_locked = []


@yorm.attr(all=Source)
class Sources(yorm.converters.List):

    """A list of source dependencies."""


@yorm.attr(all=LockedSource)
class LockedSources(Sources):

    """A list of source dependencies locked to specific revisions."""


yorm.attr(sources_locked=LockedSources)(LockedSource)


@yorm.attr(location=yorm.converters.String)
@yorm.attr(sources=Sources)
@yorm.attr(sources_locked=LockedSources)
@yorm.sync("{self.root}/{self.filename}")
class Config(ShellMixin):

    """A dictionary of dependency configuration options."""

    FILENAMES = ('gdm.yml', 'gdm.yaml', '.gdm.yml', '.gdm.yaml')

    def __init__(self, root, filename=FILENAMES[0], location='gdm_sources'):
        super().__init__()
        self.root = root
        self.filename = filename
        self.location = location
        self.sources = []
        self.sources_locked = []

    @property
    def path(self):
        """Get the full path to the configuration file."""
        return os.path.join(self.root, self.filename)

    def install_deps(self, force=False, clean=True, update=True):
        """Get all sources, recursively."""
        path = os.path.join(self.root, self.location)

        if self.indent == 0:
            common.show()

        if not os.path.isdir(path):
            self.mkdir(path)
        self.cd(path)
        common.show()

        count = 0
        if update or not self.sources_locked:
            sources = self.sources
        else:
            sources = self.sources_locked
        for source in sources:
            count += 1
            source.indent = self.indent + self.INDENT

            source.update_files(force=force, clean=clean)
            source.create_link(self.root, force=force)
            common.show()

            config = load(os.getcwd())
            if config:
                config.indent = source.indent
                count += config.install_deps(force, clean, update)

            self.cd(path, visible=False)

        return count

    def get_deps(self):
        """Yield the path, repository URL, and hash of each dependency."""
        path = os.path.join(self.root, self.location)

        if os.path.exists(path):
            self.cd(path, visible=False)
        else:
            return

        for source in self.sources:
            yield source.identify()
            config = load(os.getcwd())
            if config:
                yield from config.get_deps()

            self.cd(path, visible=False)


def load(root):
    """Load the configuration for the current project."""
    for filename in os.listdir(root):
        if filename.lower() in Config.FILENAMES:
            config = Config(root, filename)
            log.debug("loaded config: %s", config.path)
            return config

    log.debug("no config found in: %s", root)
    return None
