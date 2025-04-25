const LoadingIndicator = () => {
    return (
      <div className="flex items-center justify-center space-x-2">
        <div className="animate-pulse w-4 h-4 bg-fuchsia-500 rounded-full"></div>
        <div className="animate-pulse w-4 h-4 bg-emerald-500 rounded-full animation-delay-200"></div>
        <div className="animate-pulse w-4 h-4 bg-sky-500 rounded-full animation-delay-400"></div>
        <span className="text-gray-700 ml-2 font-medium">Researching...</span>
      </div>
    );
  };
  
  export default LoadingIndicator;
  