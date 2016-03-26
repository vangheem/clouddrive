System.register(['angular2/core', './status.service', 'angular2/http'], function(exports_1, context_1) {
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
    var core_1, status_service_1, http_1;
    var StatusComponent;
    return {
        setters:[
            function (core_1_1) {
                core_1 = core_1_1;
            },
            function (status_service_1_1) {
                status_service_1 = status_service_1_1;
            },
            function (http_1_1) {
                http_1 = http_1_1;
            }],
        execute: function() {
            StatusComponent = (function () {
                function StatusComponent(_statusService) {
                    this._statusService = _statusService;
                    this.status = null;
                }
                StatusComponent.prototype.ngOnInit = function () {
                    this.getStatus();
                };
                StatusComponent.prototype.formatDate = function (date) {
                    return moment(date + 'Z').fromNow();
                };
                StatusComponent.prototype.getStatus = function () {
                    var that = this;
                    that._statusService.getStatus()
                        .subscribe(function (status) { return that.status = status; }, function (error) { return that.errorMessage = error; });
                    setTimeout(function () {
                        that.getStatus();
                    }, 122000);
                };
                StatusComponent = __decorate([
                    core_1.Component({
                        selector: 'status-app',
                        template: "\n<div class=\"main-content\" *ngIf=\"status\">\n  <div class=\"alert alert-info\" role=\"alert\" *ngIf=\"status.what\">\n    <strong>{{status.what}}</strong> <span class=\"pat-moment\">{{formatDate(status.when)}}</span>\n  </div>\n  <div class=\"current-file\" *ngIf=\"status.what == 'Syncing files' && status.current_file\">\n    <h4>Active: {{status.current_file.filename}}</h4>\n    <div class=\"progress\">\n      <div class=\"progress-bar\" role=\"progressbar\" style=\"width: {{status.current_file.percent}}%;\">\n        {{status.current_file.percent}}%\n      </div>\n    </div>\n  </div>\n\n  <div class=\"errors\" *ngIf=\"status.errored\">\n    <h4>Errored</h4>\n    <ul *ngFor=\"#error of status.errored\">\n      <li>{{error}}</li>\n    </ul>\n  </div>\n\n  <div class=\"alert alert-success\" role=\"alert\">\n    CloudDrive is authenticated\n  </div>\n  <div class=\"alert alert-success\" role=\"alert\" *ngIf=\"status.configured\">\n    Cloud Drive Sync is configured\n  </div>\n\n</div>\n",
                        providers: [http_1.HTTP_PROVIDERS, status_service_1.StatusService]
                    }), 
                    __metadata('design:paramtypes', [status_service_1.StatusService])
                ], StatusComponent);
                return StatusComponent;
            }());
            exports_1("StatusComponent", StatusComponent);
        }
    }
});
//# sourceMappingURL=status.component.js.map