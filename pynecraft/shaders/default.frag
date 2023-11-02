#version 330 core

in vec3 block_color;
in vec2 texCoord;
flat in int blockid;
flat in int faceid;
out vec4 color;
uniform sampler2DArray imageTexture;

void main()
{
    color = texture(imageTexture, vec3(texCoord.x / 3.0 - min(faceid, 2) / 3.0, texCoord.y, blockid));
}