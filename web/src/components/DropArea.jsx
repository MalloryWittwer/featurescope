import "./droparea.css"
import { Component } from "react";
import Papa from "papaparse";

class DropArea extends Component {
    constructor(props) {
        super(props);
        this.state = {
            isDragOver: null,
            folderName: null,
            csvName: null,
            imageCount: 0,
            uiError: null,
        };
    }

    setUiError = (msg) => {
        this.setState({ uiError: msg });
    };

    processFolderFiles = (files) => {
        if (!files || !files.length) return;

        const anyPath =
            files.find((f) => f.webkitRelativePath)?.webkitRelativePath ||
            files.find((f) => f.relativePath)?.relativePath ||
            null;

        const inferredFolderName = anyPath ? anyPath.split("/")[0] : "Selected folder";

        // Find CSV file in the selected folder
        const csvFiles = files.filter((f) => {
            const name = (f.name || "").toLowerCase();
            return name.endsWith(".csv") || f.type === "text/csv";
        });

        if (csvFiles.length === 0) {
            this.setState({
                folderName: inferredFolderName,
                csvName: null,
                imageCount: 0,
                uiError: "No CSV file found in the selected folder. Please include exactly one CSV.",
            });
            return;
        }

        if (csvFiles.length > 1) {
            this.setState({
                folderName: inferredFolderName,
                csvName: null,
                imageCount: 0,
                uiError: `More than one CSV file found: ${csvFiles.map((f) => f.name).join(", ")}. Please keep only one CSV.`,
            });
            return;
        }

        const csvFile = csvFiles[0];

        // Find images in the selected folder and map relative paths (example: "images/cat.png")
        const imageFileMap = new Map();
        let imageCount = 0;

        for (const f of files) {
            const isImage =
                (f.type && f.type.startsWith("image/")) ||
                /\.(png|jpe?g|gif|webp|bmp|tiff?)$/i.test(f.name);

            if (!isImage) continue;
            imageCount += 1;

            // Normalize slashes
            const key = (f.webkitRelativePath || f.name).replaceAll("\\", "/");
            imageFileMap.set(key, f);
            imageFileMap.set(f.name, f);
        }

        if (imageCount === 0) {
            this.setState({
                folderName: inferredFolderName,
                csvName: csvFile.name,
                imageCount: 0,
                uiError: "No image files found in the selected folder.",
            });
            return;
        }

        // Parse CSV
        Papa.parse(csvFile, {
            header: true,
            skipEmptyLines: true,
            dynamicTyping: true,
            complete: (results) => {
                const rows = results.data;

                // If headers are missing / weird, results.meta.fields can help debug
                const originalDataSet = this.rowsToColumnObject(rows);
                const featureOptions = this.buildFeatureOptions(originalDataSet);

                this.setState({
                    folderName: inferredFolderName,
                    csvName: csvFile.name,
                    imageCount,
                    uiError: null,

                    // originalDataSet,
                    // featureOptions,
                    // imageFileMap,

                }, this.props.actionFnct(imageFileMap, originalDataSet, featureOptions));
            },
            error: (err) => {
                console.error("CSV parse error:", err);
                this.setState({
                    folderName: inferredFolderName,
                    csvName: csvFile.name,
                    imageCount,
                    uiError: "CSV parse error. Check the console for details.",
                });
            },
        });
    }

    handleFolderUpload = (e) => {
        const files = Array.from(e.target.files || []);
        this.processFolderFiles(files);
        e.target.value = "";
    };

    buildFeatureOptions = (originalDataSet) => {
        const excludeKeys = ["id", "image_file", "thumbnail"];
        return Object.keys(originalDataSet)
            .filter((key) => !excludeKeys.includes(key))
            .map((key) => ({ value: key, label: key }));
    };

    rowsToColumnObject = (rows) => {
        if (!rows.length) return {};
        const cols = Object.keys(rows[0]);
        const out = {};
        for (const c of cols) out[c] = [];
        for (const row of rows) {
            for (const c of cols) out[c].push(row[c] ?? null);
        }
        return out;
    };

    // --- Drag/drop UI handlers ---
    onDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!this.state.isDragOver) this.setState({ isDragOver: true });
    };

    onDragLeave = (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.setState({ isDragOver: false });
    };

    onDrop = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.setState({ isDragOver: false });

        const items = Array.from(e.dataTransfer?.items || []);
        if (items.length === 0) return;

        // Folder drag/drop support (Chromium): walk entries
        const entries = items
            .map((it) => (it.webkitGetAsEntry ? it.webkitGetAsEntry() : null))
            .filter(Boolean);

        if (entries.length === 0) {
            console.error("Drag/drop folder not supported in this browser. Use click-to-select.");
            return;
        }

        const files = await this.readAllFilesFromEntries(entries);
        this.processFolderFiles(files);
    };

    // --- Folder walking helpers (Chromium) ---
    readAllFilesFromEntries = async (entries) => {
        const out = [];
        for (const entry of entries) {
            await this.walkEntry(entry, "", out);
        }
        return out;
    };

    walkEntry = async (entry, pathPrefix, out) => {
        if (entry.isFile) {
            const file = await new Promise((resolve, reject) => {
                entry.file(resolve, reject);
            });
            // Add a stable relative path (similar to webkitRelativePath)
            file.relativePath = (pathPrefix + file.name).replaceAll("\\", "/");
            out.push(file);
            return;
        }

        if (entry.isDirectory) {
            const reader = entry.createReader();
            const dirPath = pathPrefix + entry.name + "/";
            // readEntries returns chunks
            while (true) {
                const batch = await new Promise((resolve, reject) => {
                    reader.readEntries(resolve, reject);
                });
                if (!batch || batch.length === 0) break;
                for (const child of batch) {
                    await this.walkEntry(child, dirPath, out);
                }
            }
        }
    };


    render() {
        // const { actionFnct } = this.props;
        const { isDragOver, uiError, folderName, csvName, imageCount } = this.state;

        return (
            <div className="folder-upload">
                <input
                    ref={(r) => (this.folderInput = r)}
                    className="folder-input-hidden"
                    type="file"
                    webkitdirectory="true"
                    multiple
                    onChange={this.handleFolderUpload}
                />
                <div
                    className={`dropzone ${isDragOver ? "dragover" : ""}`}
                    onClick={() => this.folderInput?.click()}
                    onDragOver={this.onDragOver}
                    onDragLeave={this.onDragLeave}
                    onDrop={this.onDrop}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") this.folderInput?.click();
                    }}
                >
                    <div className="dropzone-title">Drop an image folder here</div>
                    <div className="dropzone-subtitle">
                        or click to select a folder
                    </div>
                </div>
                <div className="upload-status">
                    {uiError ? (
                        <div className="upload-error" role="alert">
                            {uiError}
                        </div>
                    ) : folderName ? (
                        <div className="upload-ok">
                            <div><strong>Folder:</strong> {folderName}</div>
                            <div><strong>CSV:</strong> {csvName}</div>
                            <div><strong>Images:</strong> {imageCount}</div>
                        </div>
                    ) : (
                        <div className="upload-hint">
                            No folder selected
                        </div>
                    )}
                </div>
            </div>
        );
    }
}

export default DropArea;
