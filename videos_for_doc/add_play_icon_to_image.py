from PIL import Image, ImageDraw
import os
import argparse


def add_play_icon(
    input_path: str,
    output_path: str = None,
    circle_scale: float = 0.22,
    triangle_scale: float = 0.42,
    circle_color=(0, 0, 0, 140),
    triangle_color=(255, 255, 255, 255),
):
    """
    在图片正中央添加一个类似 YouTube 的播放图标。

    参数:
        input_path: 输入图片路径（PNG/JPG/JPEG）
        output_path: 输出图片路径；如果不传，会自动生成
        circle_scale: 播放按钮外圆直径占图片短边的比例
        triangle_scale: 三角形尺寸相对外圆直径的比例
        circle_color: 外圆颜色 (R, G, B, A)
        triangle_color: 三角形颜色 (R, G, B, A)
    """

    # 读取图片并转为 RGBA，方便处理透明度
    image = Image.open(input_path).convert("RGBA")
    w, h = image.size

    # 创建透明图层来画图标
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 中心点
    cx, cy = w // 2, h // 2

    # 外圆半径
    short_side = min(w, h)
    circle_diameter = short_side * circle_scale
    r = circle_diameter / 2

    # 画半透明圆
    draw.ellipse(
        (cx - r, cy - r, cx + r, cy + r),
        fill=circle_color
    )

    # 播放三角形大小
    tri_w = circle_diameter * triangle_scale
    tri_h = tri_w * 1.15

    # 为了视觉居中，三角形稍微向右偏一点
    offset_x = tri_w * 0.10

    p1 = (cx - tri_w * 0.28 + offset_x, cy - tri_h / 2)
    p2 = (cx - tri_w * 0.28 + offset_x, cy + tri_h / 2)
    p3 = (cx + tri_w * 0.55 + offset_x, cy)

    draw.polygon([p1, p2, p3], fill=triangle_color)

    # 合成
    result = Image.alpha_composite(image, overlay)

    # 自动生成输出路径
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_with_play_icon.png"

    # 如果输出是 jpg/jpeg，去掉 alpha
    ext_lower = os.path.splitext(output_path)[1].lower()
    if ext_lower in [".jpg", ".jpeg"]:
        result = result.convert("RGB")

    result.save(output_path)
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a YouTube-style play icon to the center of an image.")
    parser.add_argument("input", help="Path to input image (PNG/JPG/JPEG)")
    parser.add_argument("-o", "--output", help="Path to output image", default=None)

    args = parser.parse_args()

    #saved_path = add_play_icon(args.input, args.output)
    saved_path = add_play_icon(args.input, args.input)
    print(f"Saved new image to: {saved_path}")
