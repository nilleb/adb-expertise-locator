import AuthenticatedService from "./AuthenticatedService.js";

export default class KnowledgeService extends AuthenticatedService {
  static search(query, facets) {
    return KnowledgeService.service()
      .post("search", { query: query, facets: facets })
      .then((res) => res.data);
  }

  static getDocument(uid) {
    return KnowledgeService.service()
      .get(`document/${uid}`)
      .then((res) => res.data);
  }

  static signal(verb, uid, query, description) {
    let what = { query: query, verb: verb, uid: uid, description: description };
    return KnowledgeService.service()
      .post("signal", what)
      .then((res) => res.data);
  }

  static autocompleteSkill(prefix) {
    return KnowledgeService.service()
      .post("autocompleteSkills", { prefix: prefix })
      .then((res) => res.data);
  }

  static addSkill(email, tag) {
    return KnowledgeService.service()
      .post("saveSkill", { email: email, tag: tag })
      .then((res) => res.data);
  }
  static removeSkill(email, tag) {
    return KnowledgeService.service()
      .post("removeSkill", { email: email, tag: tag })
      .then((res) => res.data);
  }
}
