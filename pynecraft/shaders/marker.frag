#version 330 core

in vec3 block_color;
in vec2 texture_coordinate;

out vec4 color;
uniform sampler2D imageTexture;

void main()
{
    color = vec4(1.0, 0.0, 0.0, 0.0) + texture(imageTexture, texture_coordinate);
    if(color.a < 0.1)
        discard;
}