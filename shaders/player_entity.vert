#version 330 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_color;
layout (location = 2) in float in_shading;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

out vec3 frag_color;
out float frag_shading;
out vec3 frag_world_pos;

void main() {
    vec4 world_pos = m_model * vec4(in_position, 1.0);
    frag_world_pos = world_pos.xyz;
    frag_color = in_color;
    frag_shading = in_shading;
    gl_Position = m_proj * m_view * world_pos;
}
