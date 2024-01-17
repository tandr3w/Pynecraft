                self.camera.update_camera_vectors()
                self.camera.view_matrix = self.camera.get_view_matrix()
                self.camera.proj_matrix = self.camera.get_projection_matrix()