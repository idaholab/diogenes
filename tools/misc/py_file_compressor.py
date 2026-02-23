# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import file_utils as f_utils


class PyFileCompressor:
    COMPRESSION_MAGIC_SIGNATURES = {
            "\x1f\x8b\x08": "gz",
            "\x42\x5a\x68": "bz2",
            "\x50\x4b\x03\x04": "zip",
            "\x57\x69\x6e\x5a\x69\x70": "winzip",
            "\x73\x7a\xbc\xaf\x27\x1c": "7zip",
            "\x1f\x9d": "tar",
            "\x1f\xa0": "tar"
    }
    COMPRESSION_MAGIC_SINGATURE_MAX_LENGTH = max(len(x) for x in self.COMPRESSION_MAGIC_SIGNATURES)
    SUPPORTED_COMPRESSION_TYPES = ["gz", "bz2", "zip", "winzip", "7zip", "tar"]


    def __init__(self):
        pass


    def __set_compression_type(self, compression_type):
        pass


    def __get_compression_type_from_file(self, file_path):
        pass


    def compress_file(self, file_path, compression_type):
        if compression_type not in self.SUPPORTED_COMPRESSION_TYPES:
            print("Error: Requested compression type ({}) not supported".format(compression_type))
            exit()




    def decompress_file(self, file_path): 
        file_type = self.__get_compression_type_from_file(file_path)
        # self.
