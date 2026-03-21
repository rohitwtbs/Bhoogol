#version 330 core

layout (location = 0) out vec4 fragColor;

in vec3 frag_color;
in float frag_shading;
in vec3 frag_world_pos;

uniform vec3 bg_color;
uniform float water_line;

const vec3 gamma     = vec3(2.2);
const vec3 inv_gamma = 1.0 / gamma;

void main() {
    vec3 col = pow(frag_color, gamma);
    col *= frag_shading;

    // underwater tint
    if (frag_world_pos.y < water_line) col *= vec3(0.0, 0.3, 1.0);

    // distance fog (matches chunk.frag)
    float fog_dist = gl_FragCoord.z / gl_FragCoord.w;
    col = mix(col, bg_color, (1.0 - exp2(-0.00001 * fog_dist * fog_dist)));

    col = pow(col, inv_gamma);
    fragColor = vec4(col, 1.0);
}
