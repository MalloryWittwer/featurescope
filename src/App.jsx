import { Component } from "react";
import Canvas from "./components/Canvas";
import Dropdown from "./components/Dropdown";

import Papa from "papaparse";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      zoom: 300,
      canvasSizeX: null,
      canvasSizeY: null,
      pointSize: 18,
      featureOptions: [],
      featureX: null,
      featureY: null,
      originalDataSet: null,
      displayDataSet: null,
      originX: 0,
      originY: 0,
      imageFileMap: null,
    };
  }

  handleFolderUpload = (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;

    // Find CSV file in the selected folder
    const csvFiles = files.filter((f) => {
      const name = (f.name || "").toLowerCase();
      return name.endsWith(".csv") || f.type === "text/csv";
    });

    if (csvFiles.length === 0) {
      console.error("No CSV file found in the selected folder.");
      e.target.value = "";
      return;
    }

    if (csvFiles.length > 1) {
      console.error(
        `More than one CSV file found in the selected folder: ${csvFiles.map((f) => f.name).join(", ")}. Please keep only one CSV file.`
      );
      e.target.value = "";
      return;
    }

    const csvFile = csvFiles[0];

    // Find images in the selected folder and map relative paths (example: "images/cat.png")
    const imageFileMap = new Map();
    for (const f of files) {

      const isImage =
        (f.type && f.type.startsWith("image/")) ||
        /\.(png|jpe?g|gif|webp|bmp|tiff?)$/i.test(f.name);

      if (!isImage) continue;

      // Normalize slashes
      const key = (f.webkitRelativePath || f.name).replaceAll("\\", "/");
      imageFileMap.set(key, f);

      // Also map by basename as a fallback
      imageFileMap.set(f.name, f);
    }

    // Parse the CSV
    Papa.parse(csvFile, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: true,
      complete: (results) => {
        const rows = results.data;

        // If headers are missing / weird, results.meta.fields can help debug
        const originalDataSet = this.rowsToColumnObject(rows);
        const featureOptions = this.buildFeatureOptions(originalDataSet);

        this.setState({ originalDataSet, featureOptions, imageFileMap }, this.updateDataDisplay);
      },
      error: (err) => {
        console.error("CSV parse error:", err);
      },
    });

    // Allow re-selecting same folder
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

  setFeatureX = (featureX) => {
    this.setState({ featureX }, this.updateDataDisplay);
  };

  setFeatureY = (featureY) => {
    this.setState({ featureY }, this.updateDataDisplay);
  };

  onMouseWheel = (e) => {
    const zoom = Math.max(300, this.state.zoom + e.deltaY);
    const pointSize = Number.parseInt(0.06 * zoom, 10);
    this.setState({ zoom, pointSize }, this.updateDataDisplay);
  };

  updateDataDisplay = () => {
    const { originalDataSet, canvasSizeX, canvasSizeY, zoom, featureX, featureY, originX, originY } = this.state;

    if (!originalDataSet || !featureX || !featureY) {
      return;
    }

    const originalXPos = originalDataSet[featureX];
    const originalYPos = originalDataSet[featureY];

    if (!Array.isArray(originalXPos) || !Array.isArray(originalYPos)) {
      return;
    }

    const displayDataSet = [];
    const len = Math.min(originalXPos.length, originalYPos.length);

    for (let idx = 0; idx < len; idx++) {
      const id = Array.isArray(originalDataSet.id) ? originalDataSet.id[idx] : originalDataSet.id;
      const thumbnail = Array.isArray(originalDataSet.thumbnail) ? originalDataSet.thumbnail[idx] : originalDataSet.thumbnail;
      const displayXPos = ((originalXPos[idx] + originX) * canvasSizeX - canvasSizeX / 2) * (zoom / 300) + canvasSizeX / 2;
      const displayYPos = ((originalYPos[idx] + originY) * canvasSizeY - canvasSizeY / 2) * (zoom / 300) + canvasSizeY / 2;
      displayDataSet.push({ id, x: displayXPos, y: displayYPos, thumbnail });
    }

    this.setState({ displayDataSet });
  };

  getXY = (clickX, clickY) => {
    const { zoom, canvasSizeX, canvasSizeY } = this.state;
    const XY = [
      ((clickX - canvasSizeX / 2) / (zoom / 300) + canvasSizeX / 2) / canvasSizeX,
      ((clickY - canvasSizeY / 2) / (zoom / 300) + canvasSizeY / 2) / canvasSizeY,
    ];
    return XY;
  };

  onPanView = (e) => {
    const { moving, xyOrigin, originX, originY } = this.state;
    if (moving) {
      const micro = document.getElementById("tooltip");
      if (micro != null) {
        micro.classList.add("invisible");
      }
      const xyOriginNew = this.getXY(e.clientX, e.clientY);

      const [X1, Y1] = xyOriginNew;
      const [X0, Y0] = xyOrigin;

      const newOriginX = originX + (X1 - X0);
      const newOriginY = originY + (Y1 - Y0);

      this.setState(
        {
          xyOrigin: xyOriginNew,
          originX: newOriginX,
          originY: newOriginY,
        },
        this.updateDataDisplay,
      );
    }
  };

  onPointerDown = (e) => {
    document.getElementById("canvas").style.cursor = "grabbing";
    const xy = this.getXY(e.clientX, e.clientY);
    this.setState({ moving: true, xyOrigin: xy });
  };

  onPointerUp = (e) => {
    e.preventDefault();
    document.getElementById("canvas").style.cursor = "grab";
    this.setState({ moving: false });
  };

  onCanvasResize = () => {
    const canvas = document.getElementById("canvas");
    const rect = canvas.getBoundingClientRect();
    const canvasSizeX = rect.width;
    const canvasSizeY = rect.height;
    this.setState({ canvasSizeX, canvasSizeY }, this.updateDataDisplay);
  };

  setupEventListeners = () => {
    window.addEventListener("resize", this.onCanvasResize);

    document
      .getElementById("canvas")
      .addEventListener("wheel", this.onMouseWheel, { passive: true });

    document
      .getElementById("canvas")
      .addEventListener("pointerdown", this.onPointerDown);

    document
      .getElementById("canvas")
      .addEventListener("pointermove", this.onPanView);

    document
      .getElementById("canvas")
      .addEventListener("pointerup", this.onPointerUp);
  };

  componentDidMount = () => {
    this.onCanvasResize();
    this.setupEventListeners();
  };

  render = () => {
    const { pointSize, displayDataSet, originalDataSet, featureOptions, imageFileMap } = this.state;
    return (
      <div className="App">
        <div className="canvas-wrapper">
          <Canvas
            pointSize={pointSize}
            displayDataSet={displayDataSet}
            originalDataSet={originalDataSet}
            imageFileMap={imageFileMap}
          />
        </div>
        <div className="side-pannel">
          <div className="folder-upload">
            <input type="file" webkitdirectory="true" multiple onChange={this.handleFolderUpload} />
          </div>
          <div className="dropdown-wrapper">
            <Dropdown
              label={"Feature 1 (X)"}
              options={featureOptions}
              actionFnct={this.setFeatureX}
            />
            <Dropdown
              label={"Feature 2 (Y)"}
              options={featureOptions}
              actionFnct={this.setFeatureY}
            />
          </div>
        </div>
      </div>
    );
  };
}

export default App;