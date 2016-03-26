import {Component} from 'angular2/core';
import {Status} from './status';
import {StatusService} from './status.service';
import {HTTP_PROVIDERS} from 'angular2/http';

declare var moment:any;


@Component({
    selector: 'status-app',
    template: `
<div class="main-content" *ngIf="status">
  <div class="alert alert-info" role="alert" *ngIf="status.what">
    <strong>{{status.what}}</strong> <span class="pat-moment">{{formatDate(status.when)}}</span>
  </div>
  <div class="current-file" *ngIf="status.what == 'Syncing files' && status.current_file">
    <h4>Active: {{status.current_file.filename}}</h4>
    <div class="progress">
      <div class="progress-bar" role="progressbar" style="width: {{status.current_file.percent}}%;">
        {{status.current_file.percent}}%
      </div>
    </div>
  </div>

  <div class="errors" *ngIf="status.errored">
    <h4>Errored</h4>
    <ul *ngFor="#error of status.errored">
      <li>{{error}}</li>
    </ul>
  </div>

  <div class="alert alert-success" role="alert">
    CloudDrive is authenticated
  </div>
  <div class="alert alert-success" role="alert" *ngIf="status.configured">
    Cloud Drive Sync is configured
  </div>

</div>
`,
  providers: [HTTP_PROVIDERS, StatusService]
})
export class StatusComponent {
  public status: Status = null;
  errorMessage: string;

  constructor(private _statusService: StatusService) { }

  ngOnInit() {
    this.getStatus();
  }

  formatDate(date){
    return moment(date + 'Z').fromNow();
  }

  getStatus(){
    var that = this;
    that._statusService.getStatus()
      .subscribe(
        status => that.status = status,
        error =>  that.errorMessage = <any>error);
    setTimeout(function(){
      that.getStatus();
    }, 122000);
  }
}
