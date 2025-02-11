import os
import textwrap

import pytest

from conans.test.assets.sources import gen_function_cpp, gen_function_h
from conans.test.functional.toolchains.meson._base import TestMesonBase


class MesonInstall(TestMesonBase):
    _conanfile_py = textwrap.dedent("""
        import os
        import shutil
        from conan import ConanFile
        from conan.tools.meson import Meson, MesonToolchain


        class App(ConanFile):
            settings = "os", "arch", "compiler", "build_type"
            options = {"shared": [True, False], "fPIC": [True, False]}
            default_options = {"shared": False, "fPIC": True}
            exports_sources = "meson.build", "hello.cpp", "hello.h"

            def config_options(self):
                if self.settings.os == "Windows":
                    del self.options.fPIC

            def layout(self):
                self.folders.build = "build"

            def generate(self):
                tc = MesonToolchain(self)
                # https://mesonbuild.com/Release-notes-for-0-50-0.html#libdir-defaults-to-lib-when-cross-compiling
                tc.project_options["libdir"] = "lib"
                tc.generate()

            def build(self):
                meson = Meson(self)
                meson.configure()
                meson.build()

            def package(self):
                meson = Meson(self)
                meson.install()

                # https://mesonbuild.com/FAQ.html#why-does-building-my-project-with-msvc-output-static-libraries-called-libfooa
                if self.settings.compiler == 'Visual Studio' and not self.options.shared:
                    shutil.move(os.path.join(self.package_folder, "lib", "libhello.a"),
                                os.path.join(self.package_folder, "lib", "hello.lib"))

            def package_info(self):
                self.cpp_info.libs = ['hello']
        """)

    _meson_build = textwrap.dedent("""
        project('tutorial', 'cpp')
        library('hello', 'hello.cpp', install: true)
        install_headers('hello.h')
        """)

    _test_package_conanfile_py = textwrap.dedent("""
        import os
        from conan import ConanFile
        from conan.tools.cmake import CMake
        from conan.tools.layout import cmake_layout

        from conans import tools

        class TestConan(ConanFile):
            settings = "os", "compiler", "build_type", "arch"
            generators = "CMakeToolchain", "CMakeDeps"

            def layout(self):
                cmake_layout(self)

            def build(self):
                cmake = CMake(self)
                cmake.configure()
                cmake.build()

            def test(self):
                if not tools.cross_building(self):
                    cmd = os.path.join(self.cpp.build.bindirs[0], "test_package")
                    self.run(cmd)
        """)

    _test_package_cmake_lists = textwrap.dedent("""
        cmake_minimum_required(VERSION 3.1)
        project(test_package CXX)

        find_package(hello CONFIG REQUIRED)

        add_executable(${PROJECT_NAME} test_package.cpp)
        target_link_libraries(${PROJECT_NAME} hello::hello)
        """)

    @pytest.mark.tool_meson
    def test_install(self):
        hello_cpp = gen_function_cpp(name="hello")
        hello_h = gen_function_h(name="hello")
        test_package_cpp = gen_function_cpp(name="main", includes=["hello"], calls=["hello"])

        self.t.save({"conanfile.py": self._conanfile_py,
                     "meson.build": self._meson_build,
                     "hello.cpp": hello_cpp,
                     "hello.h": hello_h,
                     os.path.join("test_package", "conanfile.py"): self._test_package_conanfile_py,
                     os.path.join("test_package", "CMakeLists.txt"): self._test_package_cmake_lists,
                     os.path.join("test_package", "test_package.cpp"): test_package_cpp})

        self.t.run("create . hello/0.1@ %s" % self._settings_str)

        self._check_binary()
