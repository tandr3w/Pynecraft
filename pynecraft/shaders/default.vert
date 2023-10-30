#version 330 core

layout (location=0) in vec3 vertexPos;
layout (location=1) in float block_type;
layout (location=2) in float face_id;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

out vec3 block_color;

vec3 hash31(float p) {
    vec3 p3 = fract(vec3(p * 21.2) * vec3(0.1031, 0.1030, 0.0973));
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.xxy + p3.yyz) * p3.zyx) + 0.05;
}

void main()
{
    gl_Position = m_proj * m_view * m_model * vec4(vertexPos, 1.0);
    block_color = normalize(hash31(block_type));
}