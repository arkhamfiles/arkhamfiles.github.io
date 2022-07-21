#!/usr/bin/env python3
""" script factory for html file

Script should be given as the following form:
<!-- script: (command) (argument) -->

Currently, the following scripts are available.

insert_file (file_path): insert all components from (file_path)
generate_toc: generate table of contents

"""
import os
import re
import io
import logging

from .mics import generate_toc

class ScriptRunner():
    """script runner
    """
    def __init__(self):
        self._logger = logging.getLogger(type(self).__name__)
        self._re = re.compile("<!-- script: ([^ ]+|[^ ]+ [^ ]+) -->")

    def _insert_file(self, target: str, _: io.TextIOWrapper, arg: str) -> str:
        if not os.path.isfile(arg):
            if os.path.isfile(os.path.join('raw', arg)):
                arg = os.path.join('raw', arg)
            else:
                self._logger.warning("file not found for insert_file: %s", arg)
                return target
        with open(arg, encoding='UTF-8') as fid:
            data = fid.read()
        return data

    def _generate_toc(self, _: str, file: io.TextIOWrapper, __: str) -> str:
        current_file_position = file.tell()
        file.seek(0)
        toc = generate_toc(file)
        file.seek(current_file_position)
        return toc

    def __call__(self, target: str, file: io.TextIOWrapper) -> str:
        match = self._re.match(target)
        if match is None:
            return target
        res = match.group(1).strip().split(' ')
        cmd = res[0]
        arg = res[1] if len(res) > 1 else None

        if cmd == 'insert_file':
            return self._insert_file(target, file, arg)
        if cmd == 'generate_toc':
            return self._generate_toc(target, file, arg)
        self._logger.warning("script %s is not defined. given: %s", cmd, target)
        return target

