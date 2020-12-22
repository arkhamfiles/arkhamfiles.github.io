#!/usr/bin/env python3
""" abstract class for generator
"""

from abc import ABC, abstractmethod

class GeneratorInterface(ABC):
    """generator interface
    """
    @abstractmethod
    def __call__(self, text: str) -> str:
        """generate text

        Args:
            text (str): input

        Returns:
            str: output
        """
