find static/js -iname "*.js" -exec rm {} \; &&
find static/css -iname "*.css" -exec rm {} \; &&
find front/home/build/static/js -iname "*.js" -exec cp {} static/js/ \; &&
find front/home/build/static/css -iname "*.css" -exec cp {} static/css/ \; &&
cp front/home/build/index.html templates/list.html &&

find front/admin-cn/build/static/js -iname "*.js" -exec cp {} static/js/ \; &&
find front/admin-cn/build/static/css -iname "*.css" -exec cp {} static/css/ \;
cp front/admin-cn/build/index.html templates/manage.html  &&

find front/pchome/build/static/js -iname "*.js" -exec cp {} static/js/ \; &&
find front/pchome/build/static/css -iname "*.css" -exec cp {} static/css/ \;
cp front/pchome/build/index.html templates/listing.html  &&

git add . &&
git commit -m "$1" &&
git push