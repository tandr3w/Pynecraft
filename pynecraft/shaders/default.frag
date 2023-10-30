#version 330 core

in vec3 block_color;
out vec4 color;

void main()
{
    color = vec4(block_color, 1.0);
}