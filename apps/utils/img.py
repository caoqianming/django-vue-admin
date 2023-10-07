import os
from PIL import Image
 
def compress_image(infile, outfile='', kb=40, quality=80):
    """不改变图片尺寸压缩到指定大小
    :param infile: 压缩源文件
    :param outfile: 压缩文件保存地址
    :param kb: 压缩目标, KB
    :param step: 每次调整的压缩比率
    :param quality: 初始压缩比率
    :return: 压缩文件地址，压缩文件大小
    """
    o_size = os.path.getsize(infile)/1024
    if o_size <= kb:
        return infile
    if outfile == '':
        path, end = infile.split('.')
        outfile = path + '_compressed.' + end
    im = Image.open(infile)
    im.save(outfile, quality=quality)
    while os.path.getsize(outfile) / 1024 > kb:
        imx = Image.open(outfile)
        # Resize the image using the same aspect ratio to reduce the file size
        width, height = imx.size
        new_width = int(width * 0.9)  # You can adjust the scaling factor
        new_height = int(height * 0.9)
        imx = imx.resize((new_width, new_height), Image.ANTIALIAS)
        imx.save(outfile, quality=quality)
        # quality -= step

    return outfile, os.path.getsize(outfile) / 1024