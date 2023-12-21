import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def load_images(directory, num_images):
    images = []
    for i in range(1, num_images + 1):
        img_path = f"{directory}/picture{i}.png"
        img = cv2.imread(img_path)
        images.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))  # Převést z BGR na RGB
    return images

def create_3d_object(images, save_path=None):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for i, img in enumerate(images):
        # Předpokládá se, že obrázky mají stejnou velikost
        height, width, _ = img.shape
        x, y = np.meshgrid(range(width), range(height))
        z = np.ones_like(x) * i

        # Normalizace barev do rozsahu 0-1
        facecolors = img / 255.0

        ax.plot_surface(x, y, z, facecolors=facecolors, shade=False)

    if save_path:
        plt.savefig(save_path, bbox_inches='tight', pad_inches=0.1)
        print(f"3D objekt byl uložen do souboru: {save_path}")
    else:
        plt.show()

if __name__ == "__main__":
    image_directory = "pictures/run14"
    num_images = 30  # Upravte podle počtu vašich obrázků

    save_path = "3d_object.png"  # Specifikujte cestu a název souboru pro uložení
    images = load_images(image_directory, num_images)
    create_3d_object(images, save_path)
