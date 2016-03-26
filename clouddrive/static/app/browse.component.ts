import {Component} from 'angular2/core';
import {Status} from './status';
import {StatusService} from './status.service';
import {HTTP_PROVIDERS} from 'angular2/http';
import {BrowseService} from './browse.service';
import {Folder} from './folder';

declare var moment:any;


@Component({
    selector: 'browse-app',
    template: `
<div class="main-content" *ngIf="folder">
  <ol class="breadcrumb">
    <li *ngFor="#item of getBreadcrumbs()">
      <a href="#" (click)="onClickFolder(item.path)">{{item.name}}</a>
    </li>
  </ol>
  <table class="table table-striped">
    <thead>
      <tr>
        <th>Filename</th>
        <th>Modified</th>
        <th>Size</th>
        <th>Download/Restore</th>
      </tr>
    </thead>
    <tbody>
      <tr *ngFor="#item of folder.children">
        <td><a href="#" (click)="onClickFolder(item.path)"
               *ngIf="item.kind == 'FOLDER'">{{item.name}}</a>
            <span *ngIf="item.kind != 'FOLDER'">{{item.name}}</span>
        </td>
        <td>{{formatDate(item.modifiedDate)}}</td>
        <td>
          <span *ngIf="item.contentProperties && item.contentProperties.extension">
            {{item.contentProperties.extension}}</span>
        </td>
        <td>
          <span *ngIf="item.contentProperties && item.contentProperties.size">
            {{formatBytes(item.contentProperties.size)}}</span>
        </td>
        <td>
          <a href="#" (click)="onClickDownload(item)"
               *ngIf="item.kind != 'FOLDER'">Download</a>
          <a href="#" (click)="onClickRestore(item)"
              *ngIf="item.kind == 'FOLDER'">Restore</a>
        </td>
      </tr>
    </tbody>
  </table>
</div>
<div class="main-content" *ngIf="!folder">
  Loading...
</div>
`,
  providers: [HTTP_PROVIDERS, BrowseService]
})
export class BrowseComponent {
  public folder: Folder = null;
  public path: string = '/';
  errorMessage: string;

  constructor(private _browseService: BrowseService) { }

  ngOnInit() {
    this.getFolder();
  }

  getBreadcrumbs(){
    var crumbs = [{path: '/', name: 'Home'}];
    var parts = [''];
    this.folder.path.substring(1).split('/').forEach(function(part){
      parts.push(part);
      crumbs.push({path: parts.join('/'), name: part});
    });
    return crumbs;
  }

  formatDate(date){
    return moment(date + 'Z').fromNow();
  }

  formatBytes(bytes, decimals) {
    if(bytes == 0){
      return '0 Byte';
    }
    var k = 1000; // or 1024 for binary
    var dm = decimals + 1 || 1;
    var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    var i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }

  onClickFolder(path:string){
    this.path = path;
    this.getFolder();
  }

  onClickDownload(folder:Folder){
    this._browseService.getDownloadUrl(folder.id).subscribe(
      result =>{
        var link = document.createElement("a");
        link.href =  result.url;
        link.attributes['download'] = folder.name;
        link.target = '_blank';
        link.click();
      },
      error =>  this.errorMessage = <any>error
    );
  }

  onClickRestore(folder:Folder){

  }

  getFolder(){
    var that = this;
    that._browseService.getFolder(this.path)
      .subscribe(
        folder => that.folder = folder,
        error =>  that.errorMessage = <any>error);
  }
}
