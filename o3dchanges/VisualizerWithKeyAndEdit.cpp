// ----------------------------------------------------------------------------
// -                        Open3D: www.open3d.org                            -
// ----------------------------------------------------------------------------
// The MIT License (MIT)
//
// Copyright (c) 2018 www.open3d.org
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
// IN THE SOFTWARE.
// ----------------------------------------------------------------------------

#include "Open3D/Visualization/Visualizer/VisualizerWithKeyAndEdit.h"

#include "Open3D/Visualization/Utility/GLHelper.h"
#include "Open3D/Visualization/Utility/PointCloudPicker.h"
#include "Open3D/Visualization/Visualizer/RenderOptionWithEditing.h"
#include "Open3D/Visualization/Visualizer/ViewControlWithEditing.h"

namespace open3d {
namespace visualization {

    bool VisualizerWithKeyAndEdit::InitViewControl() {
        view_control_ptr_ =
                std::unique_ptr<ViewControlWithEditing>(new ViewControlWithEditing);
        ResetViewPoint();
        return true;
    }

    bool VisualizerWithKeyAndEdit::InitRenderOption() {
        render_option_ptr_ = std::unique_ptr<RenderOptionWithEditing>(
                new RenderOptionWithEditing);
        return true;
    }

    bool VisualizerWithKeyAndEdit::AddGeometry(
            std::shared_ptr<const geometry::Geometry> geometry_ptr) {
        if (!is_initialized_)
            return false;

        glfwMakeContextCurrent(window_);
        original_geometry_ptr_ = geometry_ptr;
        bool initialSet = geometry_ptrs_.empty();

        if (geometry_ptr->GetGeometryType() ==
            geometry::Geometry::GeometryType::Unspecified) {
            return false;
        } else if (geometry_ptr->GetGeometryType() ==
                   geometry::Geometry::GeometryType::PointCloud && initialSet) {
            auto ptr = std::make_shared<geometry::PointCloud>();
            *ptr = (const geometry::PointCloud &)*original_geometry_ptr_;
            editing_geometry_ptr_ = ptr;
            editing_geometry_renderer_ptr_ = std::make_shared<glsl::PointCloudRenderer>();
            if (! editing_geometry_renderer_ptr_->AddGeometry(editing_geometry_ptr_)) {
                return false;
            }

            ids.push_back(ptr->id_);
            indices.push_back({0, ptr->points_.size() - 1});
        } else if (geometry_ptr->GetGeometryType() ==
                   geometry::Geometry::GeometryType::PointCloud) {
            auto ptr = std::make_shared<geometry::PointCloud>();
            *ptr = (const geometry::PointCloud &)*original_geometry_ptr_;

            //add indices and id of new portion of point cloud
            ids.push_back(ptr->id_);
            indices.push_back({editing_geometry_ptr_->points_.size(), (editing_geometry_ptr_->points_.size() + ptr->points_.size()) - 1});

            //modify editing_geometry_ptr adding new points, colors, normals, classes

            editing_geometry_ptr_->points_.insert(std::end(editing_geometry_ptr_->points_), std::begin(ptr->points_), std::end(ptr->points_));

            if(ptr->HasColors())
                editing_geometry_ptr_->colors_.insert(std::end(editing_geometry_ptr_->colors_), std::begin(ptr->colors_), std::end(ptr->colors_));

            if(ptr->HasNormals())
                editing_geometry_ptr_->normals_.insert(std::end(editing_geometry_ptr_->normals_), std::begin(ptr->normals_), std::end(ptr->normals_));

            if(ptr->HasClasses())
                editing_geometry_ptr_->classes_.insert(std::end(editing_geometry_ptr_->classes_), std::begin(ptr->classes_), std::end(ptr->classes_));
        } else {
            return false;
        }

        if (initialSet){
            geometry_ptrs_.insert(editing_geometry_ptr_);
            geometry_renderer_ptrs_.insert(editing_geometry_renderer_ptr_);
            view_control_ptr_->FitInGeometry(*editing_geometry_ptr_);
            ResetViewPoint();
        }

        return UpdateGeometry();
    }

    bool VisualizerWithKeyAndEdit::RemoveGeometry(const std::string id) {
        if (!is_initialized_) {
            return false;
        }
        glfwMakeContextCurrent(window_);

        //modify editing_geometry_ptr removing points, colors, normals, classes of portion defined by id

        for(unsigned long i=0; i<ids.size(); i++){
            if(ids[i] == id){
                unsigned long min = indices[i][0];
                unsigned long max = indices[i][1];

                if(editing_geometry_ptr_->HasColors())
                    editing_geometry_ptr_->colors_.erase(editing_geometry_ptr_->colors_.begin()+min, editing_geometry_ptr_->colors_.begin()+max);

                if(editing_geometry_ptr_->HasNormals())
                    editing_geometry_ptr_->normals_.erase(editing_geometry_ptr_->normals_.begin()+min, editing_geometry_ptr_->normals_.begin()+max);

                if(editing_geometry_ptr_->HasClasses())
                    editing_geometry_ptr_->classes_.erase(editing_geometry_ptr_->classes_.begin()+min, editing_geometry_ptr_->classes_.begin()+max);

                editing_geometry_ptr_->points_.erase(editing_geometry_ptr_->points_.begin()+min, editing_geometry_ptr_->points_.begin()+max);

                //update indices
                for(unsigned long j=i; j<ids.size(); j++) {
                    indices[j][0] = indices[j][0] - (max - min);
                    indices[j][1] = indices[j][1] - (max - min);
                }

                ids.erase(ids.begin()+i);
                indices.erase(indices.begin()+i);

                //remove picked points if present and update indices of picked points
                for(unsigned long h = 0; h < pointcloud_picker_ptr_->picked_indices_.size(); h++){
                    auto value = (unsigned long) pointcloud_picker_ptr_->picked_indices_[h];
                    if(min <= value && value < max)
                        pointcloud_picker_ptr_->picked_indices_.erase (pointcloud_picker_ptr_->picked_indices_.begin()+h);
                    else if(value >= max)
                        pointcloud_picker_ptr_->picked_indices_[h] = (size_t) (value - (max - min));
                }

                return UpdateGeometry();
            }
        }

        return false;
    }

    void VisualizerWithKeyAndEdit::UpdateWindowTitle() {
        if (window_ != NULL) {
            std::string new_window_title = "CloudInterpreter";
            glfwSetWindowTitle(window_, new_window_title.c_str());
        }
    }

    void VisualizerWithKeyAndEdit::BuildUtilities() {
        Visualizer::BuildUtilities();
        bool success;

        // 2. Build pointcloud picker
        success = true;
        pointcloud_picker_ptr_ = std::make_shared<PointCloudPicker>();
        if (geometry_ptrs_.empty() ||
            pointcloud_picker_ptr_->SetPointCloud(editing_geometry_ptr_) == false) {
            success = false;
        }
        pointcloud_picker_renderer_ptr_ =
                std::make_shared<glsl::PointCloudPickerRenderer>();
        if (pointcloud_picker_renderer_ptr_->AddGeometry(pointcloud_picker_ptr_) ==
            false) {
            success = false;
        }
        if (success) {
            utility_ptrs_.push_back(pointcloud_picker_ptr_);
            utility_renderer_ptrs_.push_back(pointcloud_picker_renderer_ptr_);
        }
    }

    int VisualizerWithKeyAndEdit::PickPoint(double x, double y) {
        //TODO avere più PointCloudPickingRenderer per ogni geometria aggiunta

        auto renderer_ptr = std::make_shared<glsl::PointCloudPickingRenderer>();
        if (renderer_ptr->AddGeometry(editing_geometry_ptr_) == false) {
            return -1;
        }
        const auto &view = GetViewControl();
        // Render to FBO and disable anti-aliasing
        glDisable(GL_MULTISAMPLE);
        GLuint frame_buffer_name = 0;
        glGenFramebuffers(1, &frame_buffer_name);
        glBindFramebuffer(GL_FRAMEBUFFER, frame_buffer_name);
        GLuint fbo_texture;
        glGenTextures(1, &fbo_texture);
        glBindTexture(GL_TEXTURE_2D, fbo_texture);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, view.GetWindowWidth(),
                     view.GetWindowHeight(), 0, GL_RGBA, GL_UNSIGNED_BYTE, 0);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
        if (!GLEW_ARB_framebuffer_object) {
            // OpenGL 2.1 doesn't require this, 3.1+ does
            utility::LogError(
                    "[PickPoint] Your GPU does not provide framebuffer objects. "
                    "Use "
                    "a texture instead.\n");
            glBindFramebuffer(GL_FRAMEBUFFER, 0);
            glEnable(GL_MULTISAMPLE);
            return -1;
        }
        GLuint depth_render_buffer;
        glGenRenderbuffers(1, &depth_render_buffer);
        glBindRenderbuffer(GL_RENDERBUFFER, depth_render_buffer);
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT,
                              view.GetWindowWidth(), view.GetWindowHeight());
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                                  GL_RENDERBUFFER, depth_render_buffer);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D,
                               fbo_texture, 0);
        GLenum DrawBuffers[1] = {GL_COLOR_ATTACHMENT0};
        glDrawBuffers(1, DrawBuffers);  // "1" is the size of DrawBuffers
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
            utility::LogError("[PickPoint] Something is wrong with FBO.\n");
            glBindFramebuffer(GL_FRAMEBUFFER, 0);
            glEnable(GL_MULTISAMPLE);
            return -1;
        }
        glBindFramebuffer(GL_FRAMEBUFFER, frame_buffer_name);
        view_control_ptr_->SetViewMatrices();
        glDisable(GL_BLEND);
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE);
        glClearColor(1.0f, 1.0f, 1.0f, 0.0f);
        glClearDepth(1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        renderer_ptr->Render(GetRenderOption(), GetViewControl());
        glFinish();
        uint8_t rgba[4];
        glReadPixels((int)(x + 0.5), (int)(view.GetWindowHeight() - y + 0.5), 1, 1,
                     GL_RGBA, GL_UNSIGNED_BYTE, rgba);
        int index = GLHelper::ColorCodeToPickIndex(
                Eigen::Vector4i(rgba[0], rgba[1], rgba[2], rgba[3]));
        // Recover rendering state
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        glEnable(GL_MULTISAMPLE);
        return index;
    }

    void VisualizerWithKeyAndEdit::MouseButtonCallback(GLFWwindow *window,
                                                    int button,
                                                    int action,
                                                    int mods) {
        if (button == GLFW_MOUSE_BUTTON_RIGHT && action == GLFW_RELEASE &&
            (mods & GLFW_MOD_CONTROL) && onpick != nullptr) {
            double x, y;
            glfwGetCursorPos(window, &x, &y);
#ifdef __APPLE__
            x /= pixel_to_screen_coordinate_;
            y /= pixel_to_screen_coordinate_;
#endif
            int index = PickPoint(x, y);
            if (index == -1) {
                onpick(-1);
            } else {
                auto pcd = ((const geometry::PointCloud &)(*editing_geometry_ptr_));

                if(!pcd.classes_.empty()){
                    int classid = pcd.classes_[index];
                    onpick(classid);
                    pointcloud_picker_ptr_->picked_indices_.push_back(
                            (size_t)index);
                    is_redraw_required_ = true;
                }
            }
        } else if (button == GLFW_MOUSE_BUTTON_RIGHT &&
                   action == GLFW_RELEASE && (mods & GLFW_MOD_SHIFT)) {
            if (pointcloud_picker_ptr_->picked_indices_.empty() == false) {
                utility::LogInfo(
                        "Remove picked point #{} from pick queue.\n",
                        pointcloud_picker_ptr_->picked_indices_.back());
                pointcloud_picker_ptr_->picked_indices_.pop_back();
                is_redraw_required_ = true;
            }
        }else{
            VisualizerWithKeyCallback::MouseButtonCallback(window, button, action, mods);
        }
    }

    void VisualizerWithKeyAndEdit::RegisterOnPickCallback(std::function<void(int)> callback) {
        onpick = callback;
    }

    void VisualizerWithKeyAndEdit::KeyPressCallback(
            GLFWwindow *window, int key, int scancode, int action, int mods) {

        if(key == GLFW_KEY_I && action == GLFW_RELEASE){
            if(gaming){
                glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_NORMAL);
                view_control_ptr_->resetFirstMouse();
            }else{
                glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
            }

            gaming = !gaming;
        }else if(gaming && action != GLFW_RELEASE){
            switch (key) {
                case GLFW_KEY_W:
                    //TODO flying camera:
                    //view_control_ptr_->Look(mouse_control_.mouse_position_x, mouse_control_.mouse_position_y);
                    view_control_ptr_->Scale(-0.3);
                    break;
                case GLFW_KEY_A:
                    view_control_ptr_->Translate(1.8, 0.0);
                    break;
                case GLFW_KEY_S:
                    view_control_ptr_->Scale(0.3);
                    break;
                case GLFW_KEY_D:
                    view_control_ptr_->Translate(-1.8, 0.0);
                    break;
                default:
                    VisualizerWithKeyCallback::KeyPressCallback(window, key, scancode, action, mods);
                    break;
            }
            is_redraw_required_ = true;
        }else if(key != GLFW_KEY_W && key != GLFW_KEY_A && key != GLFW_KEY_S && key != GLFW_KEY_D){
            VisualizerWithKeyCallback::KeyPressCallback(window, key, scancode, action, mods);
        }
    }

}  // namespace visualization
}  // namespace open3d
