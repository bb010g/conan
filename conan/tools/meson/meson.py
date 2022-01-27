import os

from conan.tools.build import build_jobs
from conan.tools.meson import MesonToolchain

class Meson(object):
    def __init__(self, conanfile):
        self._conanfile = conanfile

    def run(self, cmd, *args, options=None, cmd_info_name=None, **kwargs):
        if options is None:
            options = []

        cmd = "meson" + (" {}".format(cmd) if cmd is not None else "")
        for (k, v) in options:
            if v is True:
                cmd += " {}".format(k)
            elif v is not False:
                cmd += " {} {}".format(k, v)
        for arg in args:
            cmd += " {}".format(arg)
        if cmd_info_name is not False:
            cmd_info_name = "" if cmd_info_name is None else " {}".format(cmd_info_name)
            self._conanfile.output.info("Meson{} cmd: {}".format(cmd_info_name, cmd))
        return self._conanfile.run(cmd)

    def run_setup(self, *args, options=None, cmd_info_name=None, reconfigure=None, **kwargs):
        if options is None:
            options = []
        if cmd_info_name is None:
            cmd_info_name = "setup"
        if reconfigure is None:
            reconfigure = True

        build_folder = self._conanfile.build_folder
        source_folder = self._conanfile.source_folder
        if reconfigure and os.path.exists(os.path.join(build_folder, "meson-private")):
            options.insert(0, ("--reconfigure", True))
        return self.run(
            "setup",
            '"{}"'.format(build_folder),
            '"{}"'.format(source_folder),
            *args,
            options=options,
            cmd_info_name=cmd_info_name,
            **kwargs,
        )

    def run_configure(self, *args, cmd_info_name=None, **kwargs):
        if cmd_info_name is None:
            cmd_info_name = "configure"

        build_folder = self._conanfile.build_folder
        return self.run(
            "configure",
            '"{}"'.format(build_folder),
            *args,
            cmd_info_name=cmd_info_name,
            **kwargs,
        )

    def configure(self, options=None, cmd_info_name=None, **kwargs):
        if options is None:
            options = []
        if cmd_info_name is None:
            cmd_info_name = "configure"
        generators_folder = self._conanfile.generators_folder
        cross = os.path.join(generators_folder, MesonToolchain.cross_filename)
        native = os.path.join(generators_folder, MesonToolchain.native_filename)
        if os.path.exists(cross):
            options.append(("--cross-file", '"{}"'.format(cross)))
        else:
            options.append(("--native-file", '"{}"'.format(native)))
        if self._conanfile.package_folder:
            options.append(("-D", 'prefix="{}"'.format(self._conanfile.package_folder)))
        self.run_setup(options=options, cmd_info_name=cmd_info_name, **kwargs)

    def build(self, target=None):
        meson_build_folder = self._conanfile.build_folder
        cmd = 'meson compile -C "{}"'.format(meson_build_folder)
        njobs = build_jobs(self._conanfile)
        if njobs:
            cmd += " -j{}".format(njobs)
        if target:
            cmd += " {}".format(target)
        self._conanfile.output.info("Meson build cmd: {}".format(cmd))
        self._conanfile.run(cmd)

    def install(self):
        self.configure()  # To re-do the destination package-folder
        meson_build_folder = self._conanfile.build_folder
        cmd = 'meson install -C "{}"'.format(meson_build_folder)
        self._conanfile.run(cmd)

    def test(self):
        meson_build_folder = self._conanfile.build_folder
        cmd = 'meson test -v -C "{}"'.format(meson_build_folder)
        # TODO: Do we need vcvars for test?
        # TODO: This should use conanrunenv, but what if meson itself is a build-require?
        self._conanfile.run(cmd)
