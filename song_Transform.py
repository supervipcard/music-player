# -*- coding: utf-8 -*-


# 由于带有专辑图片的MP3文件用pyglet播放会出现错误，所以需要修改MP3文件数据，删除其中的ID3信息。
def transform(files):
    srcFile = files + '.mp3'
    srcfp = open(srcFile, 'rb')
    head = srcfp.read(3).decode('utf-8')
    if head == 'ID3':
        srcfp.seek(3, 1)
        size = srcfp.read(4)
        headSize = (((size[0] & 0x7f) << 21) | ((size[1] & 0x7f) << 14) | ((size[2] & 0x7f) << 7) | (size[3] & 0x7f))
        if headSize > 3000:
            destfp = open(files + '(Y)' + '.mp3', 'wb')
            srcfp.seek(headSize, 1)
            data = srcfp.read(1024)
            while data != b'':
                destfp.write(data)    # 循环写入删除了ID3信息的MP3文件数据
                data = srcfp.read(1024)

