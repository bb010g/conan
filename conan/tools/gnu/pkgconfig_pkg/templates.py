def _get_pkgconfig_pkg_pc_template():
    return textwrap.dedent("""\
        {%- set ns = namespace(iterated=false) -%}
        {%- for variable_name, variable_value in variables -%}
        {%- set ns.iterated = true -%}
        {{ variable_name }}={{ variable_value }}
        {%- endfor -%}
        {%- if ns.iterated -%}

        {%- endif -%}
        {%- if name is defined -%}Name: {{ name }}{%- endif -%}
        {%- if version is defined -%}Version: {{ version }}{%- endif -%}
        {%- if description is defined -%}Description: {{ description }}{%- endif -%}
        {%- if url is defined -%}Url: {{ url }}{%- endif -%}
        {%- if requires is defined -%}Requires: {{ requires }}{%- endif -%}
        {%- if requires_private is defined -%}Requires.private: {{ requires_private }}{%- endif -%}
        {%- if conflicts is defined -%}Conflicts: {{ conflicts }}{%- endif -%}
        {%- if provides is defined -%}Provides: {{ provides }}{%- endif -%}
        {%- if cflags is defined -%}Cflags: {{ cflags }}{%- endif -%}
        {%- if cflags_private is defined -%}Cflags.private: {{ cflags_private }}{%- endif -%}
        {%- if libs is defined -%}Libs: {{ libs }}{%- endif -%}
        {%- if libs_private is defined -%}Libs.private: {{ libs_private }}{%- endif -%}
    """)
