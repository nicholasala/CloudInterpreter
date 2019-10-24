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

#include "Open3D/Visualization/Visualizer/Visualizer.h"
#include "Open3D/Geometry/Image.h"
#include "Open3D/Visualization/Visualizer/VisualizerWithEditing.h"
#include "Open3D/Visualization/Visualizer/VisualizerWithKeyCallback.h"
#include "Open3D/Visualization/Visualizer/VisualizerWithKeyAndEdit.h"
#include "Python/docstring.h"
#include "Python/visualization/visualization.h"
#include "Python/visualization/visualization_trampoline.h"

using namespace open3d;

// Functions have similar arguments, thus the arg docstrings may be shared
static const std::unordered_map<std::string, std::string>
        map_visualizer_docstrings = {
                {"callback_func", "The call back function."},
                {"depth_scale",
                 "Scale depth value when capturing the depth image."},
                {"do_render", "Set to ``True`` to do render."},
                {"filename", "Path to file."},
                {"geometry", "The ``Geometry`` object."},
                {"height", "Height of window."},
                {"left", "Left margin of the window to the screen."},
                {"top", "Top margin of the window to the screen."},
                {"visible", "Whether the window is visible."},
                {"width", "Width of the window."},
                {"window_name", "Window title name."},
                {"convert_to_world_coordinate",
                 "Set to ``True`` to convert to world coordinates"}};

void pybind_visualizer(py::module &m) {
    py::class_<visualization::Visualizer, PyVisualizer<>,
               std::shared_ptr<visualization::Visualizer>>
            visualizer(m, "Visualizer", "The main Visualizer class.");
    py::detail::bind_default_constructor<visualization::Visualizer>(visualizer);
    visualizer
            .def("__repr__",
                 [](const visualization::Visualizer &vis) {
                     return std::string("Visualizer with name ") +
                            vis.GetWindowName();
                 })
            .def("create_window",
                 &visualization::Visualizer::CreateVisualizerWindow,
                 "Function to create a window and initialize GLFW",
                 "window_name"_a = "Open3D", "width"_a = 1920,
                 "height"_a = 1080, "left"_a = 50, "top"_a = 50,
                 "visible"_a = true)
            .def("destroy_window",
                 &visualization::Visualizer::DestroyVisualizerWindow,
                 "Function to destroy a window")
            .def("register_animation_callback",
                 &visualization::Visualizer::RegisterAnimationCallback,
                 "Function to register a callback function for animation",
                 "callback_func"_a)
            .def("run", &visualization::Visualizer::Run,
                 "Function to activate the window")
            .def("close", &visualization::Visualizer::Close,
                 "Function to notify the window to be closed")
            .def("reset_view_point", &visualization::Visualizer::ResetViewPoint,
                 "Function to reset view point")
            .def("update_geometry", &visualization::Visualizer::UpdateGeometry,
                 "Function to update geometry")
            .def("update_renderer", &visualization::Visualizer::UpdateRender,
                 "Function to inform render needed to be updated")
            .def("poll_events", &visualization::Visualizer::PollEvents,
                 "Function to poll events")
            .def("add_geometry", &visualization::Visualizer::AddGeometry,
                 "Function to add geometry to the scene and create "
                 "corresponding shaders",
                 "geometry"_a)
            .def("remove_geometry", &visualization::Visualizer::RemoveGeometry,
                 "Function to remove geometry", "geometry"_a)
            .def("get_view_control", &visualization::Visualizer::GetViewControl,
                 "Function to retrieve the associated ``ViewControl``",
                 py::return_value_policy::reference_internal)
            .def("get_render_option",
                 &visualization::Visualizer::GetRenderOption,
                 "Function to retrieve the associated ``RenderOption``",
                 py::return_value_policy::reference_internal)
            .def("capture_screen_float_buffer",
                 &visualization::Visualizer::CaptureScreenFloatBuffer,
                 "Function to capture screen and store RGB in a float buffer",
                 "do_render"_a = false)
            .def("capture_screen_image",
                 &visualization::Visualizer::CaptureScreenImage,
                 "Function to capture and save a screen image", "filename"_a,
                 "do_render"_a = false)
            .def("capture_depth_float_buffer",
                 &visualization::Visualizer::CaptureDepthFloatBuffer,
                 "Function to capture depth in a float buffer",
                 "do_render"_a = false)
            .def("capture_depth_image",
                 &visualization::Visualizer::CaptureDepthImage,
                 "Function to capture and save a depth image", "filename"_a,
                 "do_render"_a = false, "depth_scale"_a = 1000.0)
            .def("capture_depth_point_cloud",
                 &visualization::Visualizer::CaptureDepthPointCloud,
                 "Function to capture and save local point cloud", "filename"_a,
                 "do_render"_a = false, "convert_to_world_coordinate"_a = false)
            .def("get_window_name", &visualization::Visualizer::GetWindowName);

    py::class_<visualization::VisualizerWithKeyCallback,
               PyVisualizer<visualization::VisualizerWithKeyCallback>,
               std::shared_ptr<visualization::VisualizerWithKeyCallback>>
            visualizer_key(m, "VisualizerWithKeyCallback", visualizer,
                           "Visualizer with custom key callack capabilities.");
    py::detail::bind_default_constructor<
            visualization::VisualizerWithKeyCallback>(visualizer_key);
    visualizer_key
            .def("__repr__",
                 [](const visualization::VisualizerWithKeyCallback &vis) {
                     return std::string(
                                    "VisualizerWithKeyCallback with name ") +
                            vis.GetWindowName();
                 })
            .def("register_key_callback",
                 &visualization::VisualizerWithKeyCallback::RegisterKeyCallback,
                 "Function to register a callback function for a key press "
                 "event",
                 "key"_a, "callback_func"_a);

    py::class_<visualization::VisualizerWithEditing,
               PyVisualizer<visualization::VisualizerWithEditing>,
               std::shared_ptr<visualization::VisualizerWithEditing>>
            visualizer_edit(m, "VisualizerWithEditing", visualizer,
                            "Visualizer with editing capabilities.");
    py::detail::bind_default_constructor<visualization::VisualizerWithEditing>(
            visualizer_edit);
    visualizer_edit.def(py::init<double, bool, const std::string &>())
            .def("__repr__",
                 [](const visualization::VisualizerWithEditing &vis) {
                     return std::string("VisualizerWithEditing with name ") +
                            vis.GetWindowName();
                 })
            .def("get_picked_points",
                 &visualization::VisualizerWithEditing::GetPickedPoints,
                 "Function to get picked points");

    /*VisualizerWithKeyAndEdit*/

    py::class_<visualization::VisualizerWithKeyAndEdit,
            PyVisualizer<visualization::VisualizerWithKeyAndEdit>,
            std::shared_ptr<visualization::VisualizerWithKeyAndEdit>>
            visualizer_key_and_edit(m, "VisualizerWithKeyAndEdit", visualizer_key,
                                    "Visualizer with custom key callack capabilities and editing capabilities");
    py::detail::bind_default_constructor<
            visualization::VisualizerWithKeyAndEdit>(visualizer_key_and_edit);
    visualizer_key_and_edit
            .def("__repr__",
                 [](const visualization::VisualizerWithKeyAndEdit &vis) {
                     return std::string(
                             "VisualizerWithKeyCallback with name ") +
                            vis.GetWindowName();
                 })
            .def("remove_geometry", &visualization::VisualizerWithKeyAndEdit::RemoveGeometry,
                 "Function to remove geometry by its id", "id"_a)
            .def("register_onpick_callback",
                 &visualization::VisualizerWithKeyAndEdit::RegisterOnPickCallback,
                 "Function to register a callback function for a point picking ",
                 "callback_func"_a);

    docstring::ClassMethodDocInject(m, "Visualizer", "add_geometry",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer", "remove_geometry",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer",
                                    "capture_depth_float_buffer",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer", "capture_depth_image",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer",
                                    "capture_depth_point_cloud",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer",
                                    "capture_screen_float_buffer",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer", "capture_screen_image",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer", "close",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer", "create_window",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer", "destroy_window",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer", "get_render_option",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer", "get_view_control",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer", "get_window_name",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer", "poll_events",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer",
                                    "register_animation_callback",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer", "reset_view_point",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer", "run",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer", "update_geometry",
                                    map_visualizer_docstrings);
    docstring::ClassMethodDocInject(m, "Visualizer", "update_renderer",
                                    map_visualizer_docstrings);
}

void pybind_visualizer_method(py::module &m) {}
