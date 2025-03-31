//聊天表管理增删改查
import http from './index.js'


// 获取全部聊天表的信息
export const getAllChats = (data) => {
  return http({
    url: '/chats',
    method: 'get',
    params: data
  })
};
// 获取单个聊天表的详细信息
export const getChatById = (data) => {
  return http({
    url: '/chats/' + data.id,
    method: 'get',
    params: data
  })
};

// 增加聊天表记录
export const addChat = data => {
  return http({
    url: '/chats',
    method: 'post',
    data
  })
};

// 更新聊天表记录
export const updateChat = (data) => {
  return http({
    url: '/chats/' + data.id,
    method: 'put',
    data
  })
};

// 删除聊天表记录
export const deleteChatById = id => {
  return http({
    url: '/chats/' + id,
    method: 'delete',
  })
};

