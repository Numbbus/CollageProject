import ast
import numpy as np

BITS = 5
SHIFT = 8 - BITS
LEVELS = 1 << BITS 



def quantize(rgb):
    r, g, b = rgb
    return(r >> 3, g >> 3, b >> 3)

with open(f"images/avg_rgb_values.txt", "r") as source_colors:
    allRgbVals = ast.literal_eval(source_colors.readline())
    print(allRgbVals[1910])
    sourceColors_np = np.array(allRgbVals, dtype=np.int16)
    source_colors.close()


lut = np.zeros((LEVELS, LEVELS, LEVELS), dtype=np.int16)

for r in range(LEVELS):
    for g in range(LEVELS):
        for b in range(LEVELS):
            color = np.array([
                r << SHIFT,
                g << SHIFT,
                b << SHIFT
            ])


            # Distance from this color to every source image color
            diff = sourceColors_np - color
            distances = np.sqrt(np.sum(diff * diff, axis=1))

            # Index of best-matching source image
            best_idx = np.argmin(distances)

            # Store the image index directly
            lut[r, g, b] = best_idx

print(lut[quantize((172, 93, 103))])

#np.save("lut.npy", lut)

