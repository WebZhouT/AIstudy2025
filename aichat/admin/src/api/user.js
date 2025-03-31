//用户表管理增删改查
import http from './index.js'


// 获取全部用户表的信息
export const getAllUsers = (data) => {
  return http({
    url: '/users',
    method: 'get',
    params: data
  })
};
// 获取单个用户表的详细信息
export const getUserById = (data) => {
  return http({
    url: '/users/' + data.id,
    method: 'get',
    params: data
  })
};

// 增加一个用户表记录
export const addUser = data => {
  return http({
    url: '/users',
    method: 'post',
    data
  })
};

// 更新一个用户表记录
export const updateUser = (data) => {
  return http({
    url: '/users/' + data.id,
    method: 'put',
    data
  })
};

// 删除一个用户表记录
export const deleteUserById = id => {
  return http({
    url: '/users/' + id,
    method: 'delete',
  })
};