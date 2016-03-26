import {Component} from 'angular2/core';
import {StatusComponent} from './status.component';
import {BrowseComponent} from './browse.component';
import {HTTP_PROVIDERS}    from 'angular2/http';

@Component({
  selector: 'entry-app',
  template: `
<button class="browse-button btn btn-default"
        [class.active]="browse"
        (click)="onToggleBrowse()">Browse</button>
<browse-app *ngIf="browse"></browse-app>
<status-app></status-app>
`,
  directives: [StatusComponent, BrowseComponent],
  providers: [HTTP_PROVIDERS]
})
export class AppComponent {
  public browse:boolean = false;

  onToggleBrowse(){
    this.browse = !this.browse;
  }
}
