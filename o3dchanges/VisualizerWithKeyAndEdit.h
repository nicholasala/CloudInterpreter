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

#pragma once
#include "VisualizerWithKeyCallback.h"
#include "Open3D/Geometry/PointCloud.h"

namespace open3d {

namespace visualization {

    class PointCloudPicker;

class VisualizerWithKeyAndEdit : public VisualizerWithKeyCallback{

public:
    VisualizerWithKeyAndEdit() {};
    ~VisualizerWithKeyAndEdit() override {};
    bool AddGeometry(std::shared_ptr<const geometry::Geometry> geometry_ptr) override;
    bool RemoveGeometry(std::string id);
    void BuildUtilities() override;
    void UpdateWindowTitle() override;
    int PickPoint(double x, double y);
    void RegisterOnPickCallback(std::function<void(int)> callback);

protected:
    bool InitViewControl() override;
    bool InitRenderOption() override;
    void MouseButtonCallback(GLFWwindow *window,
                             int button,
                             int action,
                             int mods) override;
    void KeyPressCallback(GLFWwindow *window,
                          int key,
                          int scancode,
                          int action,
                          int mods) override;

protected:
    std::shared_ptr<PointCloudPicker> pointcloud_picker_ptr_;
    std::shared_ptr<glsl::PointCloudPickerRenderer> pointcloud_picker_renderer_ptr_;

    std::shared_ptr<const geometry::Geometry> original_geometry_ptr_;
    std::shared_ptr<geometry::PointCloud> editing_geometry_ptr_;
    std::shared_ptr<glsl::GeometryRenderer> editing_geometry_renderer_ptr_;

    std::function<void(int)> onpick = nullptr;

    std::vector<std::string> ids;
    std::vector<std::array<unsigned long, 2>> indices;
    bool gaming = false;

};

}  // namespace visualization
}  // namespace open3d
