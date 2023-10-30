#version 330 core

layout (location=0) in vec3 vertexPos;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

void main()
{
    gl_Position = m_proj * m_view * m_model * vec4(vertexPos, 1.0);
}