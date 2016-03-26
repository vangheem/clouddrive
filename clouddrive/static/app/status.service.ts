import {Injectable} from 'angular2/core';
import {Http, Response} from 'angular2/http';
import {Status} from './status';
import {Observable} from 'rxjs/Observable';


@Injectable()
export class StatusService {
  constructor (private http: Http) {}

  private _statusUrl = '/status';

  getStatus() {
    return this.http.get(this._statusUrl)
      .map(res => <Status> res.json())
      .catch(this.handleError);
  }

  private handleError (error: Response) {
    // in a real world app, we may send the server to some remote logging infrastructure
    // instead of just logging it to the console
    console.error(error);
    return Observable.throw(error.json().error || 'Server error');
  }
}
