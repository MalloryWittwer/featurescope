import { Component } from "react";
import Canvas from "./components/Canvas";
import Dropdown from "./components/Dropdown";
import DropArea from "./components/DropArea";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      zoom: 300,
      zoomRel: 1.0,
      pointSize: 18,
      canvasSizeX: null,
      canvasSizeY: null,
      originX: 0,
      originY: 0,
      featureX: null,
      featureY: null,
      featureOptions: [],
      originalDataSet: null,
      displayDataSet: null,
      imageFileMap: null,
      xyClick01: [],
    };
  }

  onDropAreaTriggered = (imageFileMap, originalDataSet, featureOptions) => {
    this.setState({ imageFileMap, originalDataSet, featureOptions });
  }

  setFeatureX = (featureX) => {
    this.setState({ featureX }, this.updateDataDisplay);
  };

  setFeatureY = (featureY) => {
    this.setState({ featureY }, this.updateDataDisplay);
  };

  originToDisplay = (originalPosX, originalPosY) => {
    const { zoomRel, originX, originY, canvasSizeX, canvasSizeY } = this.state;
    const displayArr = [
      ((originalPosX + originX) * canvasSizeX - canvasSizeX / 2) * zoomRel + canvasSizeX / 2,
      ((originalPosY + originY) * canvasSizeY - canvasSizeY / 2) * zoomRel + canvasSizeY / 2
    ];
    return displayArr;
  }

  displayToOrigin = (displayPosX, displayPosY) => {
    const { zoomRel, canvasSizeX, canvasSizeY } = this.state;
    const originXYArr = [
      ((displayPosX - canvasSizeX / 2) / zoomRel + canvasSizeX / 2) / canvasSizeX,
      ((displayPosY - canvasSizeY / 2) / zoomRel + canvasSizeY / 2) / canvasSizeY,
    ];
    return originXYArr;
  }

  updateDataDisplay = () => {
    const {
      originalDataSet,
      featureX,
      featureY,
    } = this.state;

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
      const [displayXPos, displayYPos] = this.originToDisplay(originalXPos[idx], originalYPos[idx]);
      const id = Array.isArray(originalDataSet.id) ? originalDataSet.id[idx] : originalDataSet.id;
      const thumbnail = Array.isArray(originalDataSet.thumbnail) ? originalDataSet.thumbnail[idx] : originalDataSet.thumbnail;
      displayDataSet.push({ id, x: displayXPos, y: displayYPos, thumbnail });
    }

    this.setState({ displayDataSet });
  };

  resetDisplayBounds = () => {
    const { originX, originY, canvasSizeX, canvasSizeY } = this.state;

    const [canvasLimitX0, canvasLimitY0] = this.displayToOrigin(0, 0);
    const [canvasLimitX1, canvasLimitY1] = this.displayToOrigin(canvasSizeX, canvasSizeY);
    const clX0 = canvasLimitX0 - originX;
    const clY0 = canvasLimitY0 - originY;
    const clX1 = canvasLimitX1 - originX;
    const clY1 = canvasLimitY1 - originY;

    let noX = originX;
    let noY = originY;
    if (clX0 <= 0) {
      noX = canvasLimitX0;
    }
    if (clY0 <= 0) {
      noY = canvasLimitY0;
    }
    if (clX1 > 1) {
      noX = canvasLimitX1 - 1;
    }
    if (clY1 > 1) {
      noY = canvasLimitY1 - 1;
    }
    this.setState({ originX: noX, originY: noY }, this.updateDataDisplay)
  };

  onMouseWheel = (e) => {
    const zoom = Math.max(300, this.state.zoom + e.deltaY);
    const zoomRel = zoom / 300;
    const pointSize = Number.parseInt(0.06 * zoom, 10);
    this.setState({ zoom, zoomRel, pointSize }, this.resetDisplayBounds);
  };

  onPanView = (e) => {
    const { moving, xyClick01, originX, originY } = this.state;
    if (moving) {
      const micro = document.getElementById("tooltip");
      if (micro != null) {
        micro.classList.add("invisible");
      }
      const xyClickNew01 = this.displayToOrigin(e.clientX, e.clientY);
      const [X1, Y1] = xyClickNew01;
      const [X0, Y0] = xyClick01;

      const newOriginX = originX + (X1 - X0);
      const newOriginY = originY + (Y1 - Y0);

      this.setState({ originX: newOriginX, originY: newOriginY, xyClick01: xyClickNew01 }, this.resetDisplayBounds);
    }
  };

  onPointerDown = (e) => {
    document.getElementById("canvas").style.cursor = "grabbing";
    const xyClickNew01 = this.displayToOrigin(e.clientX, e.clientY);
    this.setState({ moving: true, xyClick01: xyClickNew01 });
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
    const {
      pointSize,
      displayDataSet,
      originalDataSet,
      featureOptions,
      imageFileMap,
    } = this.state;

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
          <div className="dropdown-wrapper">
            <DropArea
              actionFnct={this.onDropAreaTriggered}
            />
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