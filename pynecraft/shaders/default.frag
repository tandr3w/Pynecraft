#version 330 core

in vec3 block_color;
in vec2 texCoord;
in float shading;
flat in int blockid;
flat in int faceid;
out vec4 color;
uniform sampler2DArray imageTexture;

float fog_maxdist = 300.0;
float fog_mindist = 34.0;

void main()
{
    // gl_FragCoord.z / gl_FragCoord.w is the distance to the camera
    // https://opengl-notes.readthedocs.io/en/latest/topics/texturing/aliasing.html
    float dist = gl_FragCoord.z / gl_FragCoord.w;
    float fog_factor = (fog_maxdist - dist) / (fog_maxdist - fog_mindist);
    fog_factor = clamp(fog_factor, 0.0, 1.0);
    color = mix(texture(imageTexture, vec3(texCoord.x / 3.0 - min(faceid, 2) / 3.0, texCoord.y, blockid)) * shading, 
            vec4(0.52, 0.81, 0.92, 1.0),
            1-fog_factor);
}