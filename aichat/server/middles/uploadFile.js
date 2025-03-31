/* 中间件 */

const multer = require('multer')
const path = require('path');
const fs = require('fs');
/* 中间件图片文件上传 */
//自定义中间件【图片上传】
function uploadFile (req, res, next) {
  //dest 值为文件存储的路径;single方法,表示上传单个文件,参数为表单数据对应的key
  // let upload = multer({ dest: "public/uploads" }).single("photo");
  //设置文件的名称
  let filename = "";
  //获取绝对路径
  let fullPath = path.resolve(__dirname, "../public/uploads");/* 存储图片 */
  // 确保存储路径存在，如果不存在则创建
  if (!fs.existsSync(fullPath)) {
    fs.mkdirSync(fullPath, { recursive: true });
  }

  console.log(fullPath)
  let storage = multer.diskStorage({
    //设置存储路径
    destination: (req, file, cb) => {
      console.log("destination:", file);
      // cb(null,fullPath);
      cb(null, fullPath);
    },
    //设置存储的文件名
    filename: (req, file, cb) => {
      console.log("filename:", file);
      //获取文件的扩展名
      let extname = path.extname(file.originalname);
      filename = file.fieldname + "-" + Date.now() + extname;
      cb(null, filename);
    }
  })
  let upload = multer({ storage: storage }).single("file");
  /* single属性名需和上传的name一致否则报错：multererr:MulterError: */
  upload(req, res, (err) => {
    console.log(req.file);
    /* 文件存入 */
    if (err instanceof multer.MulterError) {
      res.status(400).send({ 'code': '400', message: "multererr:" + err });
      console.log("multererr:" + err);
      return false;
    } else if (err) {
      res.status(400).send({ 'code': '400', message: "multererr:" + err });
      return false;
    } else {
      //上传成功后，将图片写在req.body.photo中，继续住下执行
      // req.body.photo=filename;
      req.body.photo = filename;
      console.log({ 'filesuccess': req.file })
      next();
    }
  })
}
module.exports = {
  uploadFile: uploadFile
};
