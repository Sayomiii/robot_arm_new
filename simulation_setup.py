import pybullet as p
import pybullet_data
import time
import numpy as np

def quaternion_to_matrix(quat):
    """Convert a quaternion to a 3x3 rotation matrix."""
    x, y, z, w = quat
    return np.array([
        [1 - 2 * (y**2 + z**2), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x**2 + z**2), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x**2 + y**2)],
    ])

box_urdf_file = r"models/box.xml"

p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.8)

p.loadURDF("plane.urdf")
table_top_height = 0.625
p.loadURDF("table/table.urdf", [0, 0, 0], p.getQuaternionFromEuler([0, 0, 0]))

p.loadURDF(box_urdf_file, [0.4, 0.23, table_top_height + 0.01], p.getQuaternionFromEuler([0, 0, 0]))
p.loadURDF(box_urdf_file, [-0.4, 0.23, table_top_height + 0.01], p.getQuaternionFromEuler([0, 0, 0]))

manipulator_id = p.loadURDF("kuka_iiwa/model.urdf", [0, -0.35, table_top_height], p.getQuaternionFromEuler([0, 0, 0]))
end_effector_link_index = 6

fov, aspect, near, far = 60, 1.0, 0.02, 5.0

p.setRealTimeSimulation(1)
try:
    while True:
        p.stepSimulation()
        link_state = p.getLinkState(manipulator_id, end_effector_link_index)
        end_effector_pos = link_state[4]  # World position of the end effector
        end_effector_orn = link_state[5]  # World orientation of the end effector (quaternion)

        # Convert orientation to a rotation matrix
        rot_matrix = quaternion_to_matrix(end_effector_orn)

        # Forward vector: where the end effector is pointing
        forward_vector = rot_matrix[:, 2]  # X-axis of the rotation matrix
        camera_target = end_effector_pos + forward_vector * 0.1  # Look slightly ahead

        # Up vector: Y-axis of the rotation matrix
        up_vector = rot_matrix[:, 0]  # Z-axis of the rotation matrix (aligned with 'up')

        view_matrix = p.computeViewMatrix(end_effector_pos, camera_target, up_vector)
        projection_matrix = p.computeProjectionMatrixFOV(fov, aspect, near, far)

        width, height, rgb_image, depth_image, seg_image = p.getCameraImage(
            width=640,
            height=480,
            viewMatrix=view_matrix,
            projectionMatrix=projection_matrix
        )

        time.sleep(1. / 240.)

except KeyboardInterrupt:
    p.disconnect()
