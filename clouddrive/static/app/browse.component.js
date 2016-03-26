System.register(['angular2/core', 'angular2/http', './browse.service'], function(exports_1, context_1) {
    "use strict";
    var __moduleName = context_1 && context_1.id;
    var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
        var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
        if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
        else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
        return c > 3 && r && Object.defineProperty(target, key, r), r;
    };
    var __metadata = (this && this.__metadata) || function (k, v) {
        if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
    };
    var core_1, http_1, browse_service_1;
    var BrowseComponent;
    return {
        setters:[
            function (core_1_1) {
                core_1 = core_1_1;
            },
            function (http_1_1) {
                http_1 = http_1_1;
            },
            function (browse_service_1_1) {
                browse_service_1 = browse_service_1_1;
            }],
        execute: function() {
            BrowseComponent = (function () {
                function BrowseComponent(_browseService) {
                    this._browseService = _browseService;
                    this.folder = null;
                    this.path = '/';
                }
                BrowseComponent.prototype.ngOnInit = function () {
                    this.getFolder();
                };
                BrowseComponent.prototype.getBreadcrumbs = function () {
                    var crumbs = [{ path: '/', name: 'Home' }];
                    var parts = [''];
                    this.folder.path.substring(1).split('/').forEach(function (part) {
                        parts.push(part);
                        crumbs.push({ path: parts.join('/'), name: part });
                    });
                    return crumbs;
                };
                BrowseComponent.prototype.formatDate = function (date) {
                    return moment(date + 'Z').fromNow();
                };
                BrowseComponent.prototype.formatBytes = function (bytes, decimals) {
                    if (bytes == 0) {
                        return '0 Byte';
                    }
                    var k = 1000; // or 1024 for binary
                    var dm = decimals + 1 || 1;
                    var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
                    var i = Math.floor(Math.log(bytes) / Math.log(k));
                    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
                };
                BrowseComponent.prototype.onClickFolder = function (path) {
                    this.path = path;
                    this.getFolder();
                };
                BrowseComponent.prototype.onClickDownload = function (folder) {
                    var _this = this;
                    this._browseService.getDownloadUrl(folder.id).subscribe(function (result) {
                        var link = document.createElement("a");
                        link.href = result.url;
                        link.attributes['download'] = folder.name;
                        link.target = '_blank';
                        link.click();
                    }, function (error) { return _this.errorMessage = error; });
                };
                BrowseComponent.prototype.onClickRestore = function (folder) {
                };
                BrowseComponent.prototype.getFolder = function () {
                    var that = this;
                    that._browseService.getFolder(this.path)
                        .subscribe(function (folder) { return that.folder = folder; }, function (error) { return that.errorMessage = error; });
                };
                BrowseComponent = __decorate([
                    core_1.Component({
                        selector: 'browse-app',
                        template: "\n<div class=\"main-content\" *ngIf=\"folder\">\n  <ol class=\"breadcrumb\">\n    <li *ngFor=\"#item of getBreadcrumbs()\">\n      <a href=\"#\" (click)=\"onClickFolder(item.path)\">{{item.name}}</a>\n    </li>\n  </ol>\n  <table class=\"table table-striped\">\n    <thead>\n      <tr>\n        <th>Filename</th>\n        <th>Modified</th>\n        <th>Size</th>\n        <th>Download/Restore</th>\n      </tr>\n    </thead>\n    <tbody>\n      <tr *ngFor=\"#item of folder.children\">\n        <td><a href=\"#\" (click)=\"onClickFolder(item.path)\"\n               *ngIf=\"item.kind == 'FOLDER'\">{{item.name}}</a>\n            <span *ngIf=\"item.kind != 'FOLDER'\">{{item.name}}</span>\n        </td>\n        <td>{{formatDate(item.modifiedDate)}}</td>\n        <td>\n          <span *ngIf=\"item.contentProperties && item.contentProperties.extension\">\n            {{item.contentProperties.extension}}</span>\n        </td>\n        <td>\n          <span *ngIf=\"item.contentProperties && item.contentProperties.size\">\n            {{formatBytes(item.contentProperties.size)}}</span>\n        </td>\n        <td>\n          <a href=\"#\" (click)=\"onClickDownload(item)\"\n               *ngIf=\"item.kind != 'FOLDER'\">Download</a>\n          <a href=\"#\" (click)=\"onClickRestore(item)\"\n              *ngIf=\"item.kind == 'FOLDER'\">Restore</a>\n        </td>\n      </tr>\n    </tbody>\n  </table>\n</div>\n<div class=\"main-content\" *ngIf=\"!folder\">\n  Loading...\n</div>\n",
                        providers: [http_1.HTTP_PROVIDERS, browse_service_1.BrowseService]
                    }), 
                    __metadata('design:paramtypes', [browse_service_1.BrowseService])
                ], BrowseComponent);
                return BrowseComponent;
            }());
            exports_1("BrowseComponent", BrowseComponent);
        }
    }
});
//# sourceMappingURL=browse.component.js.map