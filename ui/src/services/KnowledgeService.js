import AuthenticatedService from './AuthenticatedService.js';

export default class KnowledgeService extends AuthenticatedService {
  static search(query) {
    return KnowledgeService.service().post('search', { query: query }).then((res) => res.data);
  }
}
