#encoding "utf-8"

JobW -> "работать" | "заниматься" | "я";

JobTitle -> (Word<gnc-agr[1]>) (Word<gnc-agr[1]>) (Word<gnc-agr[1]>) Noun<gnc-agr[1], rt> (Word<gnc-agr[1]>) (Word<gnc-agr[1]>);

Job -> JobW JobTitle interp (Job.Name);
