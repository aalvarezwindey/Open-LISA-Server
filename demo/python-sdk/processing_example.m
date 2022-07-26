img = imread('image_input.bmp');
fprintf('Original image size: [%d %d]\n', size(img));

img_resized = imresize(img, [64, NaN]);
fprintf('Resized image size: [%d %d]\n', size(img_resized));

imwrite(img_resized,'image_output.bmp');