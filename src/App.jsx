import { Component } from "react";
import Canvas from "./components/Canvas";
import Dropdown from "./components/Dropdown";

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
    };
  }

  fetchDataSet = () => {
    fetch("http://localhost:8000/dataset/")
      .then((r) => r.json())
      .then((originalDataSet) => {
        const excludeKeys = ["id", "image_file", "thumbnail"];
        const featureOptions = Object.keys(originalDataSet)
          .filter((key) => !excludeKeys.includes(key))
          .map((key) => ({ value: key, label: key }));
        this.setState({ originalDataSet, featureOptions }, this.updateDataDisplay);
      });
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
    this.fetchDataSet();
    this.onCanvasResize();
    this.setupEventListeners();
  };

  render = () => {
    const { pointSize, displayDataSet, featureOptions } = this.state;
    return (
      <div className="App">
        <div className="canvas-wrapper">
          <Canvas pointSize={pointSize} displayDataSet={displayDataSet} />
        </div>
        <div className="side-pannel">
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