import AuthenticatedService from './AuthenticatedService.js';

export default class KnowledgeService extends AuthenticatedService {
  static search(query) {
    return KnowledgeService.service().post('search', { query: query }).then((res) => res.data);
  }

  static getDocument(uid) {
    return KnowledgeService.service().get(`document/${uid}`).then((res) => res.data);
  }

  static signal(verb, uid, query, description) {
    let what = { query: query, verb: verb, uid: uid, description: description };
    return KnowledgeService.service().post('signal', what).then((res) => res.data);
  }
}
