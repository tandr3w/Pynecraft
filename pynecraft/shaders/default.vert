#version 330 core

layout (location=0) in ivec3 vertexPos;
layout (location=1) in int block_type;
layout (location=2) in int face_id;
layout (location=3) in int occ_id;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

out vec2 texCoord;
flat out int faceid;
flat out int blockid;
out float shading;

const float occ_vals[4] = float[4](0.1, 0.4, 0.7, 1.0);

const vec2 coords[12] = vec2[12](
    vec2(1, 0), vec2(1, 1), vec2(0, 1), vec2(1, 0), vec2(0, 1), vec2(0, 0), // Top, Right, Back faces
    vec2(0, 0), vec2(1, 1), vec2(0, 1), vec2(0, 0), vec2(1, 0), vec2(1, 1) // Bottom, Left, Front faces
);

void main()
{
    texCoord = coords[gl_VertexID % 6 + (face_id & 1) * 6];
    gl_Position = m_proj * m_view * m_model * vec4(vertexPos, 1);
    faceid = face_id;
    shading = occ_vals[occ_id];
    blockid = block_type;
}