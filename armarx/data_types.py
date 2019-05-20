import numpy as np



RGBA = np.dtype({'names': ['R','G','B','A'],
                 'formats': [np.uint8, np.uint8, np.uint8, np.uint8]})
Normal3D = np.dtype({"names": ["nx", "ny", "nz"],
                     "formats": [np.float32, np.float32, np.float32]})
Point3D = np.dtype({"names": ["x", "y", "z"],
                  "formats": [np.float32, np.float32, np.float32]})
OrientedPoint3D = np.dtype([("normal", Normal3D), ("point", Point3D)])
ColoredPoint3D = np.dtype([("color", RGBA), ("point", Point3D)])
ColoredLabeledPoint3D = np.dtype([("color", RGBA), ("point", Point3D), ("label", np.uint32)])
# TODO: why is the label here np.uint32 and not np.uint8? Is it the same for the other labels?
# http://docs.pointclouds.org/1.7.0/structpcl_1_1_label.html
# pcl::Label is uint_32 --> most likely in the method ConvertToPCL in armarx the label is cast to this type and this
# is responsible for the error
# can this lead to other errors in armarx? is this wanted behavior?
LabeledPoint3D = np.dtype([("point", Point3D), ("label", np.uint32)])
IntensityPoint3D = np.dtype([("point", Point3D), ("intensity", np.float32)])
