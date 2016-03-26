export interface ContentProperties{
  extension:string;
  size:number;
  md5:string;
  version:number;
  contentType:string;
}
export interface Folder {
  name:string;
  path:string;
  createdBy:string;
  createdDate:string;
  eTagResponse:string;
  id:string;
  isShared:boolean;
  kind:string;
  labels:string;
  modifiedDate:string;
  parents:string[];
  restricted:boolean;
  status:string;
  version:number;
  children:Folder[];
  contentProperties:ContentProperties;
}
