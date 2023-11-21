#version 330 core

layout (location=0) in vec3 vertexPos;
layout (location=2) in vec3 blockColor;
layout (location=2) in vec2 texCoord;

out vec2 texture_coordinate;
out vec3 block_color;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

void main()
{
    gl_Position = m_proj * m_view * m_model * vec4(vertexPos, 1.0);
    block_color = blockColor;
    texture_coordinate = texCoord;
}