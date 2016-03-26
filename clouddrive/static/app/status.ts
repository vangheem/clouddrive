export interface CurrentFile {
  filename: string;
  percent: number;
}

export interface Status {
  configured: boolean;
  what: string;
  when: string;
  current_file: CurrentFile;
  errored: string[];
  sub_folder: string;
  folders: string[];
  excluded: string[];
  update_frequency: number;
}
