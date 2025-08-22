"""
Custom exception types for the segmenting engine.
These ensure clarity in error handling throughout the pipeline.
"""


class ClipSegmentationError(Exception):
    """
    Base exception for all errors raised during the clip segmentation process.
    """
    pass


class TilingAlgorithmError(ClipSegmentationError):
    """
    Raised when the TextTiling algorithm fails due to invalid config or logic issues.
    """
    pass

"""
Custom exception types for the segmenting engine.
These ensure clarity in error handling throughout the pipeline.
"""


class ClipFinderError(ClipSegmentationError):
    """
    Raised when the ClipFinder cannot identify valid clip segments.
    """
    pass


class TextTilerError(TilingAlgorithmError):
    """
    Raised when the TextTiler algorithm encounters an error in processing.
    """
    pass
