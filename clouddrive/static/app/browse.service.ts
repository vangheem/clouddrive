import {Injectable} from 'angular2/core';
import {Http, Response} from 'angular2/http';
import {Folder} from './folder';
import {Observable} from 'rxjs/Observable';


@Injectable()
export class BrowseService {
  constructor (private http: Http) {}

  private _browseUrl = '/browse';
  private _downloadUrl = '/download';

  getFolder(path) {
    return this.http.get(this._browseUrl + '?path=' + path)
      .map(res => <Folder> res.json())
      .catch(this.handleError);
  }

  getDownloadUrl(id:string){
    return this.http.get(this._downloadUrl + '?id=' + id)
      .map(res => <any> res.json())
      .catch(this.handleError);
  }

  private handleError (error: Response) {
    // in a real world app, we may send the server to some remote logging infrastructure
    // instead of just logging it to the console
    console.error(error);
    return Observable.throw(error.json().error || 'Server error');
  }
}
