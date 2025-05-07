import request from '../request';

export function getBOMList(params) {
  return request({
    url: '/boms/',
    method: 'get',
    params
  });
}

export function getBOMDetail(id) {
  return request({
    url: `/boms/${id}/`,
    method: 'get'
  });
}

export function createBOM(data) {
  return request({
    url: '/boms/',
    method: 'post',
    data
  });
}

export function updateBOM(id, data) {
  return request({
    url: `/boms/${id}/`,
    method: 'put',
    data
  });
}

export function deleteBOM(id) {
  return request({
    url: `/boms/${id}/`,
    method: 'delete'
  });
}

export function getBOMItems(params) {
  return request({
    url: '/bom-items/',
    method: 'get',
    params
  });
}

export function createBOMItem(data) {
  return request({
    url: '/bom-items/',
    method: 'post',
    data
  });
}

export function updateBOMItem(id, data) {
  return request({
    url: `/bom-items/${id}/`,
    method: 'put',
    data
  });
}

export function deleteBOMItem(id) {
  return request({
    url: `/bom-items/${id}/`,
    method: 'delete'
  });
}